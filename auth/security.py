"""
JWT Security utilities for Airbnb webapp
Handles password hashing, token creation, and verification
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from models import User, UserSession

# Security configuration from environment
SECRET_KEY = os.getenv("SECRET_KEY", "airbnb-webapp-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Validate critical security settings
if SECRET_KEY == "airbnb-webapp-secret-key-change-in-production":
    print("WARNING: Using default SECRET_KEY! Change this in production!")

# Password hashing - Production-grade bcrypt configuration
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing in database"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),  # JWT ID for tracking
        "type": "access"  # Token type
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),
        "type": "refresh"  # Token type
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != expected_type:
            return None
            
        return payload
    except JWTError:
        return None

def refresh_access_token(refresh_token: str, db: Session) -> Optional[dict]:
    """Create new access token from valid refresh token"""
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        return None
    
    # Verify session is still active
    token_jti = payload.get("jti")
    if not is_session_active(db, token_jti):
        return None
    
    # Get user
    email = payload.get("sub")
    statement = select(User).where(User.email == email, User.is_active)
    user = db.exec(statement).first()
    
    if not user:
        return None
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
        
    return user

def create_user_session(db: Session, user_id: int, token_jti: str, 
                       ip_address: str = None, user_agent: str = None) -> UserSession:
    """Create new user session tracking"""
    session = UserSession(
        user_id=user_id,
        token_jti=token_jti,
        expires_at=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def invalidate_user_session(db: Session, token_jti: str) -> bool:
    """Invalidate a user session (logout)"""
    statement = select(UserSession).where(UserSession.token_jti == token_jti)
    session = db.exec(statement).first()
    
    if session:
        session.is_active = False
        db.add(session)
        db.commit()
        return True
    return False

def is_session_active(db: Session, token_jti: str) -> bool:
    """Check if session is still active"""
    statement = select(UserSession).where(
        UserSession.token_jti == token_jti,
        UserSession.is_active,
        UserSession.expires_at > datetime.utcnow()
    )
    session = db.exec(statement).first()
    return session is not None