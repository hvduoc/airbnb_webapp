"""
Pydantic schemas for authentication
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for creating new user"""

    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class TokenData(BaseModel):
    """Token payload data"""

    email: Optional[str] = None
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """User response (safe data only)"""

    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user"""

    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    accessible_properties: Optional[str] = None
