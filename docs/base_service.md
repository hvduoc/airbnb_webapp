# BaseService Documentation

## Overview

BaseService là foundation class cho tất cả business logic services trong Airbnb WebApp. Cung cấp user-aware permission system và property-level data filtering.

## Core Features

### 🔐 User Context & Authentication
- Automatic user context từ JWT token
- Role-based permission checking
- Property-level access control

### 🏠 Property Filtering
- Dynamic property filtering based on user access
- Support multiple property assignments
- Admin bypass cho full data access

### 🔒 Permission System
```python
# Role hierarchy
admin > manager > staff > viewer

# Permission matrix
Role     | Read | Write | Delete
---------|------|-------|-------
admin    |  ✅  |  ✅   |  ✅
manager  |  ✅  |  ✅   |  ❌
staff    |  ✅  |  📝*  |  ❌
viewer   |  ✅  |  ❌   |  ❌

* Staff có write access cho bookings/payments only
```

## Usage Examples

### Basic Service Implementation
```python
from services.base_service import BaseService

class BookingService(BaseService):
    def get_user_bookings(self):
        """Get bookings với automatic property filtering"""
        from models import Booking
        
        # Check permission
        self.require_permission("booking", "read")
        
        # Query với property filtering
        query = select(Booking)
        filtered_query = self.apply_property_filter(query, "property_id")
        
        return self.db.exec(filtered_query).all()
```

### Property-Aware Service
```python
from services.base_service import PropertyAwareService

class PropertyService(PropertyAwareService):
    def get_property_details(self, property_id: int):
        """Get property details với access validation"""
        # Validate access
        self.require_property_access(property_id)
        
        # Get property data
        return self.get_property_by_id(property_id)
```

## API Integration

### Endpoint Integration Example
```python
from fastapi import Depends
from auth.dependencies import get_current_user
from services.booking_service import BookingService

@app.get("/api/bookings")
async def get_bookings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    service = BookingService(db, user)
    bookings = service.get_user_bookings()
    return service.format_response(bookings)
```

## Testing

### Run Tests
```bash
# All tests
pytest tests/test_base_service.py -v

# Specific test
pytest tests/test_base_service.py::TestBaseService::test_admin_permissions_allowed -v
```

### Test Coverage
- ✅ Permission checks (admin, manager, staff, viewer)
- ✅ Property filtering logic
- ✅ Error handling (401, 403)
- ✅ Response formatting
- ✅ Property access validation

## Implementation Notes

### User Model Requirements
```python
class User:
    id: int
    roles: str  # Comma-separated: "admin,manager"
    property_ids: str  # Comma-separated: "1,2,3"
```

### Database Session Management
```python
# Transaction context
with service.with_transaction():
    service.db.add(new_booking)
    service.db.commit()
```

### Error Handling
- Automatic HTTP exception raising
- Consistent error response format
- User context trong error responses

## Performance Considerations

- Property filtering applied at database level
- Minimal memory overhead
- Efficient role checking với list operations
- Query optimization với proper indexing

## Security Features

- Role-based access control
- Property-level data isolation
- Permission enforcement at service layer
- Audit trail ready (user context in responses)

## Future Enhancements

- [ ] Audit logging integration
- [ ] Caching for role/property lookups
- [ ] Fine-grained permission system
- [ ] Resource-specific permission rules