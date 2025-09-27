"""
Base Service - Foundation for all business logic services
========================================================

Provides:
- Database session management  
- User context and permission checking
- Audit trail logging hooks
- Standardized response formats
- Error handling patterns
"""

from typing import Optional, Any, Dict
from sqlmodel import Session
from db import get_session_context
from models import User

class BaseService:
    """
    Base service class với user context và permission filtering
    All business logic services inherit from this class
    """
    
    def __init__(self, session: Session, user: Optional[User] = None):
        """
        Initialize service with database session and optional user context
        
        Args:
            session: SQLModel database session
            user: Optional authenticated user for permission filtering
        """
        self.session = session
        self.current_user = user
        self.user_id = user.id if user else None
        self.user_role = user.role if user else "anonymous"
        self.current_user = user  # Alias for clarity
        self.user_id = user.id if user else None
        self.user_role = user.role if user else "anonymous"th User Context Integration
Provides foundation for all business logic services with authentication
"""
from typing import Optional, List, Any, Dict
from sqlmodel import Session, select
from fastapi import HTTPException, status
from db import get_session_context
from models import User

class BaseService:
    """
    Base service class với user context và permission filtering
    All business logic services inherit from this class
    """
    
    def __init__(self, session: Session, user: Optional[User] = None):
        """
        Initialize service with database session and optional user context
        
        Args:
            session: SQLModel database session
            user: Optional authenticated user for permission filtering
        """
        self.session = session
        self.current_user = user
        self.user_id = user.id if user else None
        self.user_role = user.role if user else "anonymous"
    
    # Session đã được inject trong constructor, không cần get_session method nữa
    
    def check_permission(self, required_role: str = "user") -> bool:
        """
        Check if current user has required permission level
        
        Role hierarchy: admin > manager > user > viewer
        
        Args:
            required_role: Minimum role required
            
        Returns:
            bool: True if user has permission
        """
        if not self.current_user:
            return required_role == "anonymous"
            
        role_hierarchy = {
            "admin": 4,
            "manager": 3, 
            "user": 2,
            "viewer": 1,
            "anonymous": 0
        }
        
        user_level = role_hierarchy.get(self.user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def require_permission(self, required_role: str = "user") -> None:
        """
        Enforce permission check, raise exception if insufficient
        
        Args:
            required_role: Minimum role required
            
        Raises:
            HTTPException: 401 if not authenticated, 403 if insufficient permissions
        """
        if not self.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
            
        if not self.check_permission(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role}, Current: {self.user_role}"
            )
    
    def get_user_filter_clause(self, model_class, user_field: str = "created_by"):
        """
        Get SQLModel filter clause for user-aware data access
        
        Args:
            model_class: SQLModel class to filter
            user_field: Field name containing user ID
            
        Returns:
            Filter clause or None for admin users
        """
        if self.check_permission("admin"):
            # Admins see all data
            return None
            
        if not self.user:
            # Anonymous users see no data
            return getattr(model_class, user_field) == -1
            
        # Regular users see only their data
        return getattr(model_class, user_field) == self.user_id
    
    def log_action(self, action: str, entity: str, entity_id: Any = None, details: Dict = None) -> None:
        """
        Log user actions for audit trail (ready for future audit system)
        
        Args:
            action: Action performed (create, update, delete, view)
            entity: Entity type (booking, property, etc.)
            entity_id: ID of entity affected
            details: Additional details about the action
        """
        # TODO: Implement audit logging when audit trail system is ready
        # For now, just structure for future implementation
        log_entry = {
            "user_id": self.user_id,
            "user_role": self.user_role,
            "action": action,
            "entity": entity, 
            "entity_id": entity_id,
            "details": details or {},
            "timestamp": "datetime.utcnow()"  # Will be actual datetime in implementation
        }
        
        # Placeholder for future audit trail implementation
        pass
    
    def format_error_response(self, message: str, details: Dict = None) -> Dict:
        """
        Format consistent error response structure
        
        Args:
            message: Error message
            details: Additional error details
            
        Returns:
            Formatted error dictionary
        """
        return {
            "success": False,
            "message": message,
            "details": details or {},
            "user_context": {
                "user_id": self.user_id,
                "user_role": self.user_role
            }
        }
    
    def format_success_response(self, data: Any = None, message: str = "Success") -> Dict:
        """
        Format consistent success response structure
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Formatted success dictionary
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "user_context": {
                "user_id": self.user_id,
                "user_role": self.user_role
            }
        }