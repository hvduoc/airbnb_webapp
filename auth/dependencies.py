"""
FastAPI dependency functions for authentication
"""
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional
from models import User, UserSession
from db import get_session
from .security import verify_token, is_session_active
from .schemas import TokenData

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)
) -> Optional[str]:
    """Get token from Authorization header or cookie"""
    # Try Authorization header first
    if credentials:
        return credentials.credentials
    
    # Try cookie
    if access_token:
        # Remove "Bearer " prefix if present
        if access_token.startswith("Bearer "):
            return access_token[7:]
        return access_token
    
    return None

async def get_current_user(
    request: Request,
    db: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from request
    token = await get_token_from_request(request)
    if not token:
        raise credentials_exception
    
    # Verify token
    payload = verify_token(token, "access")
    if payload is None:
        raise credentials_exception
    
    # Extract user data
    email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    token_jti: str = payload.get("jti")
    
    if email is None or user_id is None or token_jti is None:
        raise credentials_exception
    
    # Check if session is still active
    if not is_session_active(db, token_jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (must be active)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in get_role_hierarchy(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role or higher"
            )
        return current_user
    return role_checker

def get_role_hierarchy(required_role: str) -> list[str]:
    """Get roles that can access a resource (hierarchy)"""
    hierarchy = {
        "viewer": ["viewer", "user", "manager", "admin"],
        "user": ["user", "manager", "admin"],
        "manager": ["manager", "admin"],
        "admin": ["admin"]
    }
    return hierarchy.get(required_role, [])

# Role-based dependencies
require_admin = require_role("admin")
require_manager = require_role("manager")
require_user = require_role("user")

async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_session)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise (for public endpoints)"""
    try:
        token = await get_token_from_request(request)
        if not token:
            return None
        
        payload = verify_token(token, "access")
        if payload is None:
            return None
        
        user_id: int = payload.get("user_id")
        token_jti: str = payload.get("jti")
        
        if user_id is None or token_jti is None:
            return None
        
        if not is_session_active(db, token_jti):
            return None
        
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
        
        return user if user and user.is_active else None
        
    except Exception:
        return None