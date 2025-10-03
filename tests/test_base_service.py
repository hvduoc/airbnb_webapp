"""
Unit Tests for BaseService
==========================

Test user-aware permission system và property filtering logic.
Covers: permission checks, property filtering, transaction management.

Run: pytest -v tests/test_base_service.py
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from services.base_service import BaseService, PropertyAwareService


class MockUser:
    """Mock User object for testing"""
    def __init__(self, id=1, roles="staff", property_ids="1,2,3"):
        self.id = id
        self.roles = roles
        self.property_ids = property_ids


class MockQuery:
    """Mock SQLModel query for testing"""
    def __init__(self):
        self.column_descriptions = [{'type': MockModel()}]
        self.filtered = False
        
    def where(self, condition):
        """Mock where clause"""
        self.filtered = True
        return self


class MockModel:
    """Mock model with property_id attribute"""
    def __init__(self):
        self.property_id = Mock()


class TestBaseService:
    """Test BaseService permission và filtering logic"""
    
    def setup_method(self):
        """Setup for each test"""
        self.mock_db = Mock()
        
    def test_admin_permissions_allowed(self):
        """Test: Admin user có full permissions"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = BaseService(self.mock_db, admin_user)
        
        # Act & Assert
        assert service.check_permission("property", "read") == True
        assert service.check_permission("property", "write") == True
        assert service.check_permission("property", "delete") == True
        assert service.check_permission("booking", "write") == True
        
    def test_staff_permissions_denied(self):
        """Test: Staff user bị denied delete permissions"""
        # Arrange
        staff_user = MockUser(id=2, roles="staff", property_ids="1,2")
        service = BaseService(self.mock_db, staff_user)
        
        # Act & Assert
        assert service.check_permission("property", "read") == True
        assert service.check_permission("booking", "write") == True
        assert service.check_permission("property", "delete") == False
        assert service.check_permission("payment", "delete") == False
        
    def test_viewer_permissions_read_only(self):
        """Test: Viewer chỉ có read permissions"""
        # Arrange
        viewer_user = MockUser(id=3, roles="viewer", property_ids="1")
        service = BaseService(self.mock_db, viewer_user)
        
        # Act & Assert
        assert service.check_permission("property", "read") == True
        assert service.check_permission("booking", "read") == True
        assert service.check_permission("property", "write") == False
        assert service.check_permission("booking", "write") == False
        
    def test_property_filter_correctness(self):
        """Test: Property filtering chỉ cho phép accessible properties"""
        # Arrange
        staff_user = MockUser(id=2, roles="staff", property_ids="1,2")
        service = BaseService(self.mock_db, staff_user)
        mock_query = MockQuery()
        
        # Act
        with patch.object(mock_query.column_descriptions[0]['type'], 'property_id'):
            filtered_query = service.apply_property_filter(mock_query, "property_id")
        
        # Assert
        assert filtered_query.filtered == True
        
    def test_admin_no_property_filter(self):
        """Test: Admin không bị filter properties"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2,3")
        service = BaseService(self.mock_db, admin_user)
        mock_query = MockQuery()
        
        # Act
        filtered_query = service.apply_property_filter(mock_query, "property_id")
        
        # Assert
        assert filtered_query == mock_query  # No filtering applied
        
    def test_require_permission_raises_401_no_user(self):
        """Test: require_permission raises 401 when no user"""
        # Arrange
        service = BaseService(self.mock_db, user=None)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.require_permission("property", "read")
        assert exc_info.value.status_code == 401
        
    def test_require_permission_raises_403_insufficient(self):
        """Test: require_permission raises 403 for insufficient permissions"""
        # Arrange
        viewer_user = MockUser(id=3, roles="viewer", property_ids="1")
        service = BaseService(self.mock_db, viewer_user)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.require_permission("property", "delete")
        assert exc_info.value.status_code == 403
        
    def test_property_ids_parsing(self):
        """Test: Property IDs được parse correctly từ string"""
        # Arrange
        user = MockUser(id=1, roles="staff", property_ids="1,2,3,5")
        service = BaseService(self.mock_db, user)
        
        # Act & Assert
        assert service.user_property_ids == [1, 2, 3, 5]
        
    def test_property_ids_empty_string(self):
        """Test: Empty property_ids string returns empty list"""
        # Arrange
        user = MockUser(id=1, roles="staff", property_ids="")
        service = BaseService(self.mock_db, user)
        
        # Act & Assert
        assert service.user_property_ids == []
        
    def test_format_response_structure(self):
        """Test: format_response returns correct structure"""
        # Arrange
        user = MockUser(id=1, roles="staff", property_ids="1,2")
        service = BaseService(self.mock_db, user)
        
        # Act
        response = service.format_response({"test": "data"}, "Test message")
        
        # Assert
        assert response["success"] == True
        assert response["message"] == "Test message"
        assert response["data"]["test"] == "data"
        assert response["user_context"]["user_id"] == 1
        assert response["user_context"]["roles"] == ["staff"]
        

class TestPropertyAwareService:
    """Test PropertyAwareService specialized methods"""
    
    def setup_method(self):
        """Setup for each test"""
        self.mock_db = Mock()
        
    def test_validate_property_access_admin(self):
        """Test: Admin có access to all properties"""
        # Arrange
        admin_user = MockUser(id=1, roles="admin", property_ids="1,2")
        service = PropertyAwareService(self.mock_db, admin_user)
        
        # Act & Assert
        assert service.validate_property_access(1) == True
        assert service.validate_property_access(999) == True  # Admin sees all
        
    def test_validate_property_access_staff(self):
        """Test: Staff chỉ có access to assigned properties"""
        # Arrange
        staff_user = MockUser(id=2, roles="staff", property_ids="1,2")
        service = PropertyAwareService(self.mock_db, staff_user)
        
        # Act & Assert
        assert service.validate_property_access(1) == True
        assert service.validate_property_access(2) == True
        assert service.validate_property_access(3) == False
        
    def test_require_property_access_raises_403(self):
        """Test: require_property_access raises 403 for unauthorized property"""
        # Arrange
        staff_user = MockUser(id=2, roles="staff", property_ids="1,2")
        service = PropertyAwareService(self.mock_db, staff_user)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            service.require_property_access(3)
        assert exc_info.value.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])