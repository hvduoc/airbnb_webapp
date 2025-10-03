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

from typing import Any, Dict, Optional

from sqlmodel import Session

from models import User


class BaseService:
    """
    Base service class with user context and permission filtering
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
    
    def check_permission(self, required_role: str = "user") -> bool:
        """
        Check if current user has required permission level
        
        Role hierarchy: admin > manager > user > anonymous
        
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
    
    def log_activity(self, action: str, details: Dict[str, Any] = None):
        """
        Log user activity for audit trail
        
        Args:
            action: Action name/type
            details: Additional details to log
        """
        # Audit logging implementation - can be extended
        if details is None:
            details = {}
            
        
        # TODO: Implement actual audit logging (database, file, etc.)
        # For now just pass - will be implemented when audit system is ready
        pass
    
    def success_response(self, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Standardized success response format
        
        Args:
            message: Success message
            data: Optional response data
            
        Returns:
            Standardized success response dict
        """
        response = {
            "success": True,
            "message": message
        }
        
        if data:
            response["data"] = data
            
        return response
    
    def error_response(self, message: str, status_code: int = 400, 
                      details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Standardized error response format
        
        Args:
            message: Error message
            status_code: HTTP status code
            details: Optional error details
            
        Returns:
            Standardized error response dict
        """
        response = {
            "success": False,
            "error": message,
            "status_code": status_code
        }
        
        if details:
            response["details"] = details
            
        return response
    
    def get_user_filter_clause(self, model_class, user_field: str = "user_id"):
        """
        Get user-specific filter clause for queries
        Useful for multi-tenant scenarios
        
        Args:
            model_class: SQLModel class to filter
            user_field: Field name for user filtering
            
        Returns:
            Filter clause or None if no user context
        """
        if not self.current_user:
            return None
            
        # For admin users, no filtering needed
        if self.user_role == "admin":
            return None
            
        # For regular users, filter by user_id
        return getattr(model_class, user_field) == self.user_id
    
    def apply_user_filtering(self, query, model_class, user_field: str = "user_id"):
        """
        Apply user-specific filtering to query
        
        Args:
            query: SQLModel query to filter
            model_class: Model class being queried
            user_field: Field name for user filtering
            
        Returns:
            Filtered query
        """
        filter_clause = self.get_user_filter_clause(model_class, user_field)
        
        if filter_clause is not None:
            query = query.where(filter_clause)
            
        return query