"""
Authentication routes for Airbnb webapp
Handles login, logout, registration, and user management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta
from models import User, UserSession
from db import get_session
from auth.security import (
    authenticate_user, create_access_token, get_password_hash,
    create_user_session, invalidate_user_session, ACCESS_TOKEN_EXPIRE_MINUTES
)
from auth.dependencies import get_current_active_user, require_admin, get_optional_current_user
from auth.schemas import UserCreate, UserLogin, Token, UserResponse, UserUpdate
import json

router = APIRouter(prefix="/auth", tags=["authentication"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Display login page"""
    return templates.TemplateResponse("auth_login.html", {
        "request": request,
        "error": error
    })

@router.post("/login")
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session)
):
    """Handle login form submission"""
    # Authenticate user
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("auth_login.html", {
            "request": request,
            "error": "Email hoặc mật khẩu không đúng"
        })
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(
        data=access_token_data, expires_delta=access_token_expires
    )
    
    # Track session
    from jose import jwt
    payload = jwt.decode(access_token, options={"verify_signature": False})
    token_jti = payload.get("jti")
    
    create_user_session(
        db=db,
        user_id=user.id,
        token_jti=token_jti,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # Create response with redirect
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    # Set secure httpOnly cookie for web app
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response

@router.get("/logout")
async def logout():
    """Logout user"""
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_admin)  # Only admin can create users
):
    """Register new user (admin only)"""
    # Check if user already exists
    statement = select(User).where(
        (User.email == user.email) | (User.username == user.username)
    )
    existing_user = db.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        accessible_properties="[]"  # Empty by default
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """Login user and return JWT token"""
    # Authenticate user (using email as username)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }
    access_token = create_access_token(
        data=access_token_data, expires_delta=access_token_expires
    )
    
    # Track session
    from jose import jwt
    payload = jwt.decode(access_token, options={"verify_signature": False})
    token_jti = payload.get("jti")
    
    create_user_session(
        db=db,
        user_id=user.id,
        token_jti=token_jti,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """Logout user and invalidate session"""
    # This would need the current token JTI - simplified for now
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """List all users (admin only)"""
    statement = select(User)
    users = db.exec(statement).all()
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """Update user (admin only)"""
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.accessible_properties is not None:
        user.accessible_properties = user_update.accessible_properties
    
    user.updated_at = datetime.utcnow()
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_session)
):
    """Delete user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.username} deleted successfully"}

@router.get("/check")
async def check_auth_status(
    current_user: User = Depends(get_optional_current_user)
):
    """Check authentication status (public endpoint)"""
    if current_user:
        return {
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "username": current_user.username,
                "role": current_user.role
            }
        }
    else:
        return {"authenticated": False}