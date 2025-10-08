"""
Base Service for User-Aware Business Logic
==========================================

Foundation service class với user context và property-level filtering.
All business logic services inherit từ BaseService để có consistent
permission checking và data access control.

Author: Airbnb WebApp Team
Created: 2025-10-03 for PROJ-008
"""

from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from models import User


class BaseService:
    """
    Base service class với user context và permission filtering.

    Provides:
    - User authentication context
    - Property-level data filtering
    - Permission checking by role/resource
    - Transaction management
    - Consistent error handling
    """

    def __init__(self, db: Session, user: Optional[User] = None):
        """
        Initialize service với database session và user context.

        Args:
            db: SQLModel database session
            user: Authenticated user for permission filtering
        """
        self.db = db
        self.user = user
        self.user_id = user.id if user else None
        self.user_roles = user.roles.split(",") if user and user.roles else []
        self.user_property_ids = self._parse_property_ids(user)

    def _parse_property_ids(self, user: Optional[User]) -> List[int]:
        """Parse user's accessible property IDs từ user.property_ids"""
        if not user or not user.property_ids:
            return []
        try:
            # Giả định property_ids là "1,2,3" format
            return [
                int(pid.strip()) for pid in user.property_ids.split(",") if pid.strip()
            ]
        except (ValueError, AttributeError):
            return []

    def check_permission(self, resource: str, action: str = "read") -> bool:
        """
        Check if current user có permission cho resource/action.

        Role hierarchy: admin > manager > staff > viewer

        Args:
            resource: Resource type (property, booking, payment, etc.)
            action: Action type (read, write, delete)

        Returns:
            bool: True if user has permission
        """
        if not self.user:
            return False

        # Admin có full access
        if "admin" in self.user_roles:
            return True

        # Manager có read/write access
        if "manager" in self.user_roles:
            return action in ["read", "write"]

        # Staff có read access + limited write
        if "staff" in self.user_roles:
            if action == "read":
                return True
            # Staff có thể write bookings/payments nhưng không delete
            if action == "write" and resource in ["booking", "payment"]:
                return True
            return False

        # Viewer chỉ có read access
        if "viewer" in self.user_roles:
            return action == "read"

        return False

    def require_permission(self, resource: str, action: str = "read") -> None:
        """
        Enforce permission check, raise HTTPException if insufficient.

        Args:
            resource: Resource type
            action: Action type

        Raises:
            HTTPException: 401 if not authenticated, 403 if insufficient permissions
        """
        if not self.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if not self.check_permission(resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {action} on {resource}",
            )

    def apply_property_filter(self, query, model_property_attr: str = "property_id"):
        """
        Apply property-level filtering based on user's accessible properties.

        Args:
            query: SQLModel query to filter
            model_property_attr: Attribute name on model (e.g., "property_id")

        Returns:
            Filtered query hoặc unfiltered nếu admin
        """
        # Admin sees all data
        if "admin" in self.user_roles:
            return query

        # Other roles chỉ thấy properties họ có access
        if self.user_property_ids:
            # Dynamic attribute access cho flexibility
            if hasattr(query.column_descriptions[0]["type"], model_property_attr):
                property_column = getattr(
                    query.column_descriptions[0]["type"], model_property_attr
                )
                return query.where(property_column.in_(self.user_property_ids))

        # Nếu user không có property access, return empty result
        return query.where(False)

    @contextmanager
    def with_transaction(self):
        """
        Transaction context manager for consistent database operations.

        Usage:
            with service.with_transaction():
                # database operations
                service.db.add(obj)
                service.db.commit()
        """
        try:
            yield self.db
            # Transaction will be committed by caller
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database operation failed: {str(e)}",
            )

    def format_response(self, data: Any = None, message: str = "Success") -> Dict:
        """
        Format consistent API response structure.

        Args:
            data: Response data
            message: Success message

        Returns:
            Formatted response dictionary
        """
        return {
            "success": True,
            "message": message,
            "data": data,
            "user_context": {
                "user_id": self.user_id,
                "roles": self.user_roles,
                "property_access": self.user_property_ids,
            },
        }

    def format_error(self, message: str, details: Optional[Dict] = None) -> Dict:
        """
        Format consistent error response structure.

        Args:
            message: Error message
            details: Additional error details

        Returns:
            Formatted error dictionary
        """
        response = {
            "success": False,
            "message": message,
            "user_context": {"user_id": self.user_id, "roles": self.user_roles},
        }

        if details:
            response["details"] = details

        return response


class PropertyAwareService(BaseService):
    """
    Specialized base service cho property-related operations.
    Extends BaseService với property-specific helper methods.
    """

    def get_accessible_properties(self):
        """Get list of properties user có access tới."""
        from models import Property

        query = select(Property)

        # Apply property filtering
        if "admin" not in self.user_roles:
            if self.user_property_ids:
                query = query.where(Property.id.in_(self.user_property_ids))
            else:
                # No property access
                return []

        return self.db.exec(query).all()

    def validate_property_access(self, property_id: int) -> bool:
        """
        Validate if user có access to specific property.

        Args:
            property_id: Property ID to check

        Returns:
            bool: True if user has access
        """
        if "admin" in self.user_roles:
            return True

        return property_id in self.user_property_ids

    def require_property_access(self, property_id: int) -> None:
        """
        Enforce property access check.

        Args:
            property_id: Property ID to check

        Raises:
            HTTPException: 403 if no access to property
        """
        if not self.validate_property_access(property_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access to property {property_id}",
            )
