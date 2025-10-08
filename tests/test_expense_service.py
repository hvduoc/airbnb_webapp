"""
Unit Tests for ExpenseService
=============================

Test expense service với user-aware permissions và property filtering.
Covers: create expense, permission checks, property filtering, summary aggregations.

Run: pytest -v tests/test_expense_service.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi import HTTPException

from services.expense_service import ExpenseService


class MockUser:
    """Mock User object for testing"""

    def __init__(self, id=1, roles="staff", property_ids="1,2,3"):
        self.id = id
        self.roles = roles
        self.property_ids = property_ids


class MockExpense:
    """Mock Expense object"""

    def __init__(
        self,
        id=1,
        amount=500000,
        category_id=1,
        property_id=1,
        vendor="Test Vendor",
        date="2025-10-03",
        month="2025-10",
    ):
        self.id = id
        self.amount = amount
        self.category_id = category_id
        self.property_id = property_id
        self.vendor = vendor
        self.date = date
        self.month = month
        self.note = "Test expense"
        self.allocation_method = "direct"
        self.created_at = datetime.utcnow()


class MockExpenseCategory:
    """Mock ExpenseCategory object"""

    def __init__(self, id=1, name="Maintenance"):
        self.id = id
        self.name = name


class MockProperty:
    """Mock Property object"""

    def __init__(self, id=1, property_name="Test Property"):
        self.id = id
        self.property_name = property_name


class MockQueryResult:
    """Mock aggregation query result"""

    def __init__(
        self,
        property_id=1,
        property_name="Test Property",
        expense_count=5,
        total_amount=2500000,
        avg_amount=500000,
    ):
        self.property_id = property_id
        self.property_name = property_name
        self.expense_count = expense_count
        self.total_amount = total_amount
        self.avg_amount = avg_amount
        self.first_expense = "2025-10-01"
        self.last_expense = "2025-10-31"


class TestExpenseService:
    """Test ExpenseService functionality và permissions"""

    def setup_method(self):
        """Setup for each test"""
        self.mock_db = Mock()

    def test_create_expense_success(self):
        """Test: Admin user tạo expense thành công"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = ExpenseService(self.mock_db, admin_user)

        expense_data = {
            "amount": 500000,
            "category_id": 1,
            "property_id": 1,
            "vendor": "Test Vendor",
            "note": "Test expense",
            "date": "2025-10-03",
        }

        # Mock category exists
        mock_category = MockExpenseCategory()
        service.db.exec.return_value.first.return_value = mock_category

        # Mock property access check
        mock_property = MockProperty()

        # Mock database operations
        mock_expense = MockExpense()
        service.db.add = Mock()
        service.db.commit = Mock()
        service.db.refresh = Mock()
        service.db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)

        with patch.object(service, "require_permission") as mock_permission:
            with patch.object(service, "apply_property_filter") as mock_filter:
                mock_filter.return_value = Mock()
                mock_filter.return_value = Mock()  # Simulated filtered query
                service.db.exec.return_value.first.side_effect = [
                    mock_category,
                    mock_property,
                ]

                # Act
                result = service.create_expense(expense_data)

        # Assert
        mock_permission.assert_called_once_with("expense", "create")
        assert result["success"] == True
        assert result["expense"]["amount"] == 500000
        assert "VNĐ" in result["expense"]["amount_formatted"]
        assert "successfully" in result["message"]

    def test_create_expense_permission_denied(self):
        """Test: Viewer user bị denied create expense"""
        # Arrange
        viewer_user = MockUser(id=2, roles="viewer", property_ids="1")
        service = ExpenseService(self.mock_db, viewer_user)

        expense_data = {"amount": 500000, "category_id": 1, "date": "2025-10-03"}

        # Mock permission denial
        with patch.object(
            service,
            "require_permission",
            side_effect=HTTPException(
                status_code=403, detail="Insufficient permission: expense/create"
            ),
        ):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.create_expense(expense_data)
            assert exc_info.value.status_code == 403
            assert "expense" in exc_info.value.detail.lower()

    def test_create_expense_invalid_payload(self):
        """Test: Invalid payload validation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = ExpenseService(self.mock_db, admin_user)

        # Missing required fields
        invalid_data = {
            "vendor": "Test Vendor"
            # Missing amount, category_id, date
        }

        with patch.object(service, "require_permission"):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.create_expense(invalid_data)
            assert exc_info.value.status_code == 400
            assert "Missing required fields" in exc_info.value.detail

    def test_create_expense_invalid_amount(self):
        """Test: Invalid amount validation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = ExpenseService(self.mock_db, admin_user)

        # Zero amount
        invalid_data = {"amount": 0, "category_id": 1, "date": "2025-10-03"}

        with patch.object(service, "require_permission"):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.create_expense(invalid_data)
            assert exc_info.value.status_code == 400
            assert "must be greater than 0" in exc_info.value.detail

    def test_create_expense_property_access_denied(self):
        """Test: Property access denied for restricted user"""
        # Arrange
        staff_user = MockUser(
            id=3, roles="staff", property_ids="1,2"
        )  # No access to property 3
        service = ExpenseService(self.mock_db, staff_user)

        expense_data = {
            "amount": 500000,
            "category_id": 1,
            "property_id": 3,  # User doesn't have access
            "date": "2025-10-03",
        }

        # Mock category exists
        mock_category = MockExpenseCategory()
        service.db.exec.return_value.first.return_value = mock_category

        with patch.object(service, "require_permission"):
            with patch.object(service, "apply_property_filter") as mock_filter:
                # Mock no accessible property returned
                mock_filter.return_value = Mock()
                service.db.exec.return_value.first.side_effect = [
                    mock_category,
                    None,
                ]  # No property access

                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    service.create_expense(expense_data)
                assert exc_info.value.status_code == 403
                assert "Access denied" in exc_info.value.detail

    def test_list_expenses_property_filtering(self):
        """Test: List expenses với property filtering"""
        # Arrange
        staff_user = MockUser(id=3, roles="staff", property_ids="1,2")
        service = ExpenseService(self.mock_db, staff_user)

        # Mock query results
        mock_expenses = [
            type(
                "obj",
                (object,),
                {
                    "id": 1,
                    "amount": 500000,
                    "vendor": "Vendor A",
                    "note": "Note 1",
                    "date": "2025-10-01",
                    "month": "2025-10",
                    "allocation_method": "direct",
                    "created_at": datetime.utcnow(),
                    "category_name": "Maintenance",
                    "property_name": "Property 1",
                },
            )(),
            type(
                "obj",
                (object,),
                {
                    "id": 2,
                    "amount": 300000,
                    "vendor": "Vendor B",
                    "note": "Note 2",
                    "date": "2025-10-02",
                    "month": "2025-10",
                    "allocation_method": "direct",
                    "created_at": datetime.utcnow(),
                    "category_name": "Utilities",
                    "property_name": "Property 2",
                },
            )(),
        ]

        # Mock count query
        service.db.exec.return_value.first.return_value = (2, 800000)  # count, sum
        service.db.exec.return_value.all.return_value = mock_expenses

        with patch.object(service, "require_permission"):
            with patch.object(
                service, "apply_property_filter", side_effect=lambda q, attr: q
            ):
                # Act
                result = service.list_expenses()

        # Assert
        assert len(result["expenses"]) == 2
        assert result["total_count"] == 2
        assert result["total_amount"] == 800000
        assert "VNĐ" in result["total_amount_formatted"]
        assert result["expenses"][0]["amount"] == 500000

    def test_summary_by_property_aggregation(self):
        """Test: Summary aggregation correctness"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = ExpenseService(self.mock_db, admin_user)

        # Mock aggregation results
        mock_results = [
            MockQueryResult(
                property_id=1,
                property_name="Property 1",
                expense_count=10,
                total_amount=5000000,
                avg_amount=500000,
            ),
            MockQueryResult(
                property_id=2,
                property_name="Property 2",
                expense_count=8,
                total_amount=3200000,
                avg_amount=400000,
            ),
            MockQueryResult(
                property_id=3,
                property_name="Property 3",
                expense_count=5,
                total_amount=1500000,
                avg_amount=300000,
            ),
        ]
        service.db.exec.return_value.all.return_value = mock_results

        with patch.object(service, "require_permission"):
            with patch.object(
                service, "apply_property_filter", side_effect=lambda q, attr: q
            ):
                # Act
                result = service.summary_by_property()

        # Assert summary calculations
        summary = result["summary"]
        assert summary["total_properties"] == 3
        assert summary["total_expenses"] == 23  # 10 + 8 + 5
        assert summary["total_amount"] == 9700000  # 5M + 3.2M + 1.5M
        assert summary["avg_expense_per_property"] == 9700000 / 3

        # Assert properties sorted by amount (descending)
        properties = result["properties"]
        assert properties[0]["property_name"] == "Property 1"
        assert properties[0]["total_amount"] == 5000000
        assert properties[1]["total_amount"] == 3200000
        assert properties[2]["total_amount"] == 1500000

        # Assert formatting
        assert "VNĐ" in properties[0]["amount_formatted"]

    def test_no_user_context_denied(self):
        """Test: No user context raises 401"""
        # Arrange
        service = ExpenseService(self.mock_db, user=None)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.create_expense(
                {"amount": 500000, "category_id": 1, "date": "2025-10-03"}
            )
        assert exc_info.value.status_code == 401

    def test_invalid_date_format(self):
        """Test: Invalid date format validation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = ExpenseService(self.mock_db, admin_user)

        expense_data = {
            "amount": 500000,
            "category_id": 1,
            "date": "2025/10/03",  # Wrong format
        }

        with patch.object(service, "require_permission"):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.create_expense(expense_data)
            assert exc_info.value.status_code == 400
            assert "Invalid date format" in exc_info.value.detail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
