"""
Authentication Service for Payment Ledger
Provides JWT-based authentication with role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlmodel import Session, select
import jwt
import os
from functools import wraps

from db import get_session
from models import User
from services.google_sheets.models import PaymentUser, UserRole, LoginRequest, TokenResponse

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 8 * 60  # 8 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

class AuthService:
    """Authentication service for payment system"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
        """Authenticate user by username and password"""
        # Get user from database
        statement = select(User).where(
            (User.username == username) | (User.email == username)
        ).where(User.is_active == True)
        
        user = session.exec(statement).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.add(user)
        session.commit()
        
        return user
    
    @staticmethod
    def user_to_payment_user(user: User) -> PaymentUser:
        """Convert User model to PaymentUser for payments system"""
        # Parse accessible properties from JSON string
        import json
        try:
            accessible_properties = json.loads(user.accessible_properties or "[]")
        except:
            accessible_properties = []
        
        # Map role to UserRole enum
        role_mapping = {
            "user": UserRole.ASSISTANT,
            "admin": UserRole.OWNER,
            "manager": UserRole.MANAGER,
            "viewer": UserRole.ASSISTANT
        }
        
        return PaymentUser(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=role_mapping.get(user.role, UserRole.ASSISTANT),
            is_active=user.is_active,
            accessible_properties=accessible_properties
        )

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> PaymentUser:
    """Get current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = AuthService.verify_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
    except Exception:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.username == username).where(User.is_active == True)
    user = session.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    return AuthService.user_to_payment_user(user)

def require_role(allowed_roles: List[UserRole]):
    """Decorator to require specific roles"""
    def decorator(current_user: PaymentUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return decorator

# Authentication routes
from fastapi import APIRouter

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Login and get access token"""
    
    # Authenticate user
    user = await AuthService.authenticate_user(
        login_data.username, 
        login_data.password, 
        session
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=AuthService.user_to_payment_user(user)
    )

@auth_router.get("/me", response_model=PaymentUser)
async def get_current_user_info(
    current_user: PaymentUser = Depends(get_current_user)
):
    """Get current user information"""
    return current_user

@auth_router.post("/logout")
async def logout(
    current_user: PaymentUser = Depends(get_current_user)
):
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}

# Export auth service instance
auth_service = AuthService()