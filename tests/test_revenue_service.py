"""
Unit Tests for RevenueService
=============================

Test revenue service với user-aware permissions và property filtering.
Covers: permission checks, property filtering, revenue aggregation, API integration.

Run: pytest -v tests/test_revenue_service.py
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch
from fastapi import HTTPException

from services.revenue_service import RevenueService


class MockUser:
    """Mock User object for testing"""

    def __init__(self, id=1, roles="staff", property_ids="1,2,3"):
        self.id = id
        self.roles = roles
        self.property_ids = property_ids


class MockBooking:
    """Mock Booking object"""

    def __init__(
        self,
        id=1,
        property_id=1,
        total_amount=1000000,
        checkin_date=date(2025, 10, 1),
        checkout_date=date(2025, 10, 3),
        status="confirmed",
    ):
        self.id = id
        self.property_id = property_id
        self.total_amount = total_amount
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.status = status


class MockProperty:
    """Mock Property object"""

    def __init__(self, id=1, property_name="Test Property"):
        self.id = id
        self.property_name = property_name


class MockQueryResult:
    """Mock SQLModel query result"""

    def __init__(
        self,
        property_id=1,
        property_name="Test Property",
        total_bookings=5,
        total_revenue=5000000,
        avg_booking_value=1000000,
        first_booking=date(2025, 10, 1),
        last_booking=date(2025, 10, 31),
    ):
        self.property_id = property_id
        self.property_name = property_name
        self.total_bookings = total_bookings
        self.total_revenue = total_revenue
        self.avg_booking_value = avg_booking_value
        self.first_booking = first_booking
        self.last_booking = last_booking


class TestRevenueService:
    """Test RevenueService permission và revenue calculations"""

    def setup_method(self):
        """Setup for each test"""
        self.mock_db = Mock()

    def test_admin_revenue_access_allowed(self):
        """Test: Admin user có access to revenue data"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = RevenueService(self.mock_db, admin_user)

        # Mock query results
        mock_results = [
            MockQueryResult(
                property_id=1, property_name="Property 1", total_revenue=3000000
            ),
            MockQueryResult(
                property_id=2, property_name="Property 2", total_revenue=2000000
            ),
        ]
        service.db.exec.return_value.all.return_value = mock_results

        # Mock apply_property_filter to return query unchanged (admin bypass)
        with patch.object(
            service, "apply_property_filter", side_effect=lambda q, attr: q
        ):
            # Act
            result = service.revenue_by_property()

        # Assert
        assert result["summary"]["total_properties"] == 2
        assert result["summary"]["total_revenue"] == 5000000
        assert len(result["properties"]) == 2

    def test_staff_revenue_access_denied_insufficient_role(self):
        """Test: Viewer user bị denied revenue access"""
        # Arrange
        viewer_user = MockUser(id=2, roles="viewer", property_ids="1")
        service = RevenueService(self.mock_db, viewer_user)

        # Mock require_permission to raise HTTPException
        with patch.object(
            service,
            "require_permission",
            side_effect=HTTPException(
                status_code=403, detail="Insufficient permission: revenue/read"
            ),
        ):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.revenue_by_property()
            assert exc_info.value.status_code == 403
            assert "revenue" in exc_info.value.detail.lower()

    def test_property_filtering_correctness(self):
        """Test: Property filtering chỉ cho phép accessible properties"""
        # Arrange
        staff_user = MockUser(id=3, roles="staff", property_ids="1,2")
        service = RevenueService(self.mock_db, staff_user)

        # Mock results for accessible properties only
        mock_results = [
            MockQueryResult(
                property_id=1, property_name="Accessible 1", total_revenue=1000000
            ),
            MockQueryResult(
                property_id=2, property_name="Accessible 2", total_revenue=2000000
            ),
        ]
        service.db.exec.return_value.all.return_value = mock_results

        # Mock property filtering behavior
        with patch.object(service, "apply_property_filter") as mock_filter:
            mock_filter.return_value = Mock()
            mock_filter.return_value = Mock()  # Simulated filtered query

            # Act
            result = service.revenue_by_property()

            # Assert filtering was applied
            mock_filter.assert_called_once()
            assert result["summary"]["total_properties"] == 2

            # Verify only accessible properties returned
            property_ids = [p["property_id"] for p in result["properties"]]
            assert 1 in property_ids
            assert 2 in property_ids

    def test_revenue_aggregation_correctness(self):
        """Test: Revenue aggregation calculations are correct"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = RevenueService(self.mock_db, admin_user)

        # Mock detailed revenue data
        mock_results = [
            MockQueryResult(
                property_id=1,
                property_name="High Revenue Property",
                total_bookings=10,
                total_revenue=5000000,
                avg_booking_value=500000,
            ),
            MockQueryResult(
                property_id=2,
                property_name="Medium Revenue Property",
                total_bookings=8,
                total_revenue=3200000,
                avg_booking_value=400000,
            ),
            MockQueryResult(
                property_id=3,
                property_name="Low Revenue Property",
                total_bookings=5,
                total_revenue=1500000,
                avg_booking_value=300000,
            ),
        ]
        service.db.exec.return_value.all.return_value = mock_results

        with patch.object(
            service, "apply_property_filter", side_effect=lambda q, attr: q
        ):
            # Act
            result = service.revenue_by_property()

        # Assert aggregations
        summary = result["summary"]
        assert summary["total_properties"] == 3
        assert summary["total_bookings"] == 23  # 10 + 8 + 5
        assert summary["total_revenue"] == 9700000  # 5M + 3.2M + 1.5M
        assert summary["avg_revenue_per_property"] == 9700000 / 3

        # Assert properties sorted by revenue (descending)
        properties = result["properties"]
        assert properties[0]["property_name"] == "High Revenue Property"
        assert properties[0]["total_revenue"] == 5000000
        assert properties[1]["total_revenue"] == 3200000
        assert properties[2]["total_revenue"] == 1500000

        # Assert formatting
        assert "5,000,000 VNĐ" in properties[0]["revenue_formatted"]

    def test_date_filtering_applied(self):
        """Test: Start/end date filters được apply correctly"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1")
        service = RevenueService(self.mock_db, admin_user)

        mock_results = [MockQueryResult(total_revenue=1000000)]
        service.db.exec.return_value.all.return_value = mock_results

        start_date = date(2025, 10, 1)
        end_date = date(2025, 10, 31)

        with patch.object(
            service, "apply_property_filter", side_effect=lambda q, attr: q
        ):
            # Act
            result = service.revenue_by_property(
                start_date=start_date, end_date=end_date
            )

        # Assert date period recorded
        period = result["summary"]["period"]
        assert period["start_date"] == "2025-10-01"
        assert period["end_date"] == "2025-10-31"

    def test_no_user_context_denied(self):
        """Test: No user context raises 401"""
        # Arrange
        service = RevenueService(self.mock_db, user=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.revenue_by_property()
        assert exc_info.value.status_code == 401

    def test_empty_results_handled(self):
        """Test: Empty revenue results được handle gracefully"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1")
        service = RevenueService(self.mock_db, admin_user)

        # Mock empty results
        service.db.exec.return_value.all.return_value = []

        with patch.object(
            service, "apply_property_filter", side_effect=lambda q, attr: q
        ):
            # Act
            result = service.revenue_by_property()

        # Assert empty state handled
        assert result["summary"]["total_properties"] == 0
        assert result["summary"]["total_revenue"] == 0
        assert result["summary"]["avg_revenue_per_property"] == 0
        assert result["properties"] == []

    def test_include_cancelled_bookings_parameter(self):
        """Test: include_cancelled parameter affects filtering"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1")
        service = RevenueService(self.mock_db, admin_user)

        mock_results = [MockQueryResult()]
        service.db.exec.return_value.all.return_value = mock_results

        with patch.object(
            service, "apply_property_filter", side_effect=lambda q, attr: q
        ):
            # Act - include cancelled
            result_with_cancelled = service.revenue_by_property(include_cancelled=True)
            result_without_cancelled = service.revenue_by_property(
                include_cancelled=False
            )

        # Assert parameter recorded
        assert result_with_cancelled["summary"]["period"]["include_cancelled"] == True
        assert (
            result_without_cancelled["summary"]["period"]["include_cancelled"] == False
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
