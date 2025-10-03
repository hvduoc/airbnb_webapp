"""
Unit Tests for AnalyticsService
===============================

Test analytics service với dashboard KPIs và business intelligence.
Covers: revenue vs expense, occupancy metrics, ARPU, monthly trends.

Run: pytest -v tests/test_analytics_service.py
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
from fastapi import HTTPException

from services.analytics_service import AnalyticsService
from models import User


class MockUser:
    """Mock User object for testing"""
    def __init__(self, id=1, roles="staff", property_ids="1,2,3"):
        self.id = id
        self.roles = roles
        self.property_ids = property_ids


class TestAnalyticsService:
    """Test AnalyticsService dashboard functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.mock_db = Mock()
        
    def test_revenue_vs_expense_dashboard_success(self):
        """Test: Revenue vs Expense dashboard data generation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = AnalyticsService(self.mock_db, admin_user)
        
        # Mock revenue service data
        mock_revenue_data = {
            "summary": {"total_revenue": 5000000, "total_bookings": 10},
            "properties": [
                {"property_id": 1, "property_name": "Property 1", "total_revenue": 3000000},
                {"property_id": 2, "property_name": "Property 2", "total_revenue": 2000000}
            ]
        }
        
        # Mock expense service data
        mock_expense_data = {
            "summary": {"total_amount": 1500000},
            "properties": [
                {"property_id": 1, "property_name": "Property 1", "total_amount": 1000000},
                {"property_id": 2, "property_name": "Property 2", "total_amount": 500000}
            ]
        }
        
        with patch.object(service, 'require_permission'):
            with patch('services.analytics_service.RevenueService') as MockRevenueService:
                with patch('services.analytics_service.ExpenseService') as MockExpenseService:
                    # Setup mocks
                    MockRevenueService.return_value.revenue_by_property.return_value = mock_revenue_data
                    MockExpenseService.return_value.summary_by_property.return_value = mock_expense_data
                    
                    # Act
                    result = service.get_revenue_vs_expense_dashboard()
        
        # Assert
        assert result["summary"]["total_revenue"] == 5000000
        assert result["summary"]["total_expenses"] == 1500000
        assert result["summary"]["net_profit"] == 3500000
        assert result["summary"]["profit_margin"] == 70.0  # (3500000/5000000)*100
        
        # Check properties data
        assert len(result["properties"]) == 2
        prop1 = result["properties"][0]  # Should be sorted by margin
        assert prop1["property_id"] == 2  # Higher margin property first
        assert prop1["profit"] == 1500000  # 2000000 - 500000
        assert prop1["margin"] == 75.0    # (1500000/2000000)*100
        
        # Check charts data
        assert len(result["charts"]["property_names"]) == 2
        assert len(result["charts"]["revenue_chart"]) == 2
        assert len(result["charts"]["expense_chart"]) == 2
        
    def test_occupancy_metrics_calculation(self):
        """Test: Occupancy rates calculation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2")
        service = AnalyticsService(self.mock_db, admin_user)
        
        # Mock database query results
        mock_results = [
            type('obj', (object,), {
                'property_id': 1,
                'property_name': 'Property 1',
                'total_bookings': 5,
                'nights_booked': 20,  # 20 nights out of 30 days = 66.67%
                'avg_stay_length': 4.0
            })(),
            type('obj', (object,), {
                'property_id': 2,
                'property_name': 'Property 2',
                'total_bookings': 3,
                'nights_booked': 15,  # 15 nights out of 30 days = 50%
                'avg_stay_length': 5.0
            })()
        ]
        
        service.db.exec.return_value.all.return_value = mock_results
        
        with patch.object(service, 'require_permission'):
            with patch.object(service, 'apply_property_filter', side_effect=lambda q, attr: q):
                # Act
                start_date = date(2025, 10, 1)
                end_date = date(2025, 10, 30)  # 30 days
                result = service.get_occupancy_metrics(start_date, end_date)
        
        # Assert summary
        assert result["summary"]["total_nights_booked"] == 35  # 20 + 15
        assert result["summary"]["total_nights_available"] == 60  # 2 properties * 30 days
        assert result["summary"]["overall_occupancy"] == 58.33  # (35/60)*100
        assert result["summary"]["average_length_of_stay"] == 4.38  # 35/8 bookings
        
        # Assert properties
        assert len(result["properties"]) == 2
        # Should be sorted by occupancy rate (descending)
        assert result["properties"][0]["occupancy_rate"] == 66.67  # Property 1
        assert result["properties"][1]["occupancy_rate"] == 50.0   # Property 2
        
    def test_arpu_metrics_calculation(self):
        """Test: ARPU calculations accuracy"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2")
        service = AnalyticsService(self.mock_db, admin_user)
        
        # Mock revenue service data
        mock_revenue_data = {
            "summary": {"total_revenue": 6000000, "total_bookings": 12, "period": {"start_date": None, "end_date": None}},
            "properties": [
                {"property_id": 1, "property_name": "High ARPU Property", "total_revenue": 4000000, "total_bookings": 5},
                {"property_id": 2, "property_name": "Low ARPU Property", "total_revenue": 2000000, "total_bookings": 7}
            ]
        }
        
        with patch.object(service, 'require_permission'):
            with patch('services.analytics_service.RevenueService') as MockRevenueService:
                MockRevenueService.return_value.revenue_by_property.return_value = mock_revenue_data
                
                # Act
                result = service.get_arpu_metrics()
        
        # Assert overall ARPU
        assert result["summary"]["overall_arpu"] == 500000  # 6000000/12
        assert result["summary"]["total_revenue"] == 6000000
        assert result["summary"]["total_bookings"] == 12
        
        # Assert properties ARPU (sorted by ARPU descending)
        assert len(result["properties"]) == 2
        assert result["properties"][0]["property_name"] == "High ARPU Property"
        assert result["properties"][0]["arpu"] == 800000  # 4000000/5
        assert result["properties"][0]["rank"] == 1
        
        assert result["properties"][1]["property_name"] == "Low ARPU Property"
        assert result["properties"][1]["arpu"] == 285714  # 2000000/7 (rounded)
        assert result["properties"][1]["rank"] == 2
        
    def test_monthly_trends_generation(self):
        """Test: Monthly trends data generation"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2")
        service = AnalyticsService(self.mock_db, admin_user)
        
        # Mock revenue query results
        mock_revenue_results = [
            type('obj', (object,), {
                'start_date': '2025-09-15',  # Will be grouped as 2025-09
                'monthly_revenue': 2000000,
                'monthly_bookings': 5
            })(),
            type('obj', (object,), {
                'start_date': '2025-10-10',  # Will be grouped as 2025-10
                'monthly_revenue': 3000000,
                'monthly_bookings': 8
            })()
        ]
        
        # Mock expense query results
        mock_expense_results = [
            type('obj', (object,), {
                'month': '2025-09',
                'monthly_expenses': 800000
            })(),
            type('obj', (object,), {
                'month': '2025-10',
                'monthly_expenses': 1200000
            })()
        ]
        
        # Setup mock to return different results for different queries
        service.db.exec.return_value.all.side_effect = [mock_revenue_results, mock_expense_results]
        
        with patch.object(service, 'require_permission'):
            with patch.object(service, 'apply_property_filter', side_effect=lambda q, attr: q):
                # Act
                result = service.get_monthly_trends(months_back=2)
        
        # Assert trends data
        assert len(result["months"]) == 2
        assert len(result["revenue_trend"]) == 2
        assert len(result["expense_trend"]) == 2
        assert len(result["profit_trend"]) == 2
        
        # Check growth calculations
        revenue_growth = result["summary"]["revenue_growth"]
        expense_growth = result["summary"]["expense_growth"]
        
        # Growth from first to last month
        # Revenue: (3000000 - 2000000) / 2000000 * 100 = 50%
        # Expense: (1200000 - 800000) / 800000 * 100 = 50%
        assert revenue_growth == 50.0
        assert expense_growth == 50.0
        
    def test_analytics_permission_denied(self):
        """Test: Analytics permission denial"""
        # Arrange
        viewer_user = MockUser(id=2, roles="viewer", property_ids="1")
        service = AnalyticsService(self.mock_db, viewer_user)
        
        # Mock permission denial
        with patch.object(service, 'require_permission', side_effect=HTTPException(status_code=403, detail="Insufficient permission: analytics/read")):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.get_revenue_vs_expense_dashboard()
            assert exc_info.value.status_code == 403
            assert "analytics" in exc_info.value.detail.lower()
            
    def test_empty_data_handling(self):
        """Test: Empty data graceful handling"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = AnalyticsService(self.mock_db, admin_user)
        
        # Mock empty data
        mock_empty_revenue = {"summary": {"total_revenue": 0, "total_bookings": 0}, "properties": []}
        mock_empty_expense = {"summary": {"total_amount": 0}, "properties": []}
        
        with patch.object(service, 'require_permission'):
            with patch('services.analytics_service.RevenueService') as MockRevenueService:
                with patch('services.analytics_service.ExpenseService') as MockExpenseService:
                    MockRevenueService.return_value.revenue_by_property.return_value = mock_empty_revenue
                    MockExpenseService.return_value.summary_by_property.return_value = mock_empty_expense
                    
                    # Act
                    result = service.get_revenue_vs_expense_dashboard()
        
        # Assert empty state handled gracefully
        assert result["summary"]["total_revenue"] == 0
        assert result["summary"]["total_expenses"] == 0
        assert result["summary"]["net_profit"] == 0
        assert result["summary"]["profit_margin"] == 0
        assert result["properties"] == []
        assert result["charts"]["property_names"] == []
        
    def test_no_user_context_denied(self):
        """Test: No user context raises 401"""
        # Arrange
        service = AnalyticsService(self.mock_db, user=None)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.get_revenue_vs_expense_dashboard()
        assert exc_info.value.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])