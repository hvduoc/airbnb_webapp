"""
Dịch vụ Xác thực và Quản lý Người dùng - Airbnb WebApp
Xử lý đăng nhập, đăng ký, quản lý người dùng với bảo mật cấp production
Tích hợp hoàn toàn với hệ thống bảo mật chính của ứng dụng
"""

import os
import secrets
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from logging_config import log_security_event
from models import User  # Sử dụng models chính của hệ thống

# Cấu hình bảo mật từ environment - Production ready với tăng cường bảo mật
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Tạo SECRET_KEY tự động nếu không có trong environment
    SECRET_KEY = secrets.token_urlsafe(64)
    print("🔐 Đã tạo SECRET_KEY tự động. Hãy lưu vào environment variables:")
    print(f"export SECRET_KEY='{SECRET_KEY}'")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # Giảm từ 60 xuống 30 phút
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Cấu hình bảo mật tăng cường
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
ACCOUNT_LOCKOUT_DURATION = int(os.getenv("ACCOUNT_LOCKOUT_DURATION", "300"))  # 5 phút
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
REQUIRE_STRONG_PASSWORD = os.getenv("REQUIRE_STRONG_PASSWORD", "true").lower() == "true"

# Cảnh báo bảo mật trong development
if os.getenv("ENVIRONMENT", "development") == "development":
    print("🔧 Chế độ Development - Bảo mật cơ bản được kích hoạt")
else:
    print("🔒 Chế độ Production - Bảo mật cao cấp được kích hoạt")

# Mã hóa mật khẩu với cấu hình bcrypt production chuẩn
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS  # Cấu hình rounds từ environment
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác minh mật khẩu người dùng"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Mã hóa mật khẩu với bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Tạo JWT access token với thông tin bảo mật đầy đủ"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Thêm các trường JWT chuẩn
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),  # JWT ID để theo dõi
        "type": "access"  # Loại token
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Tạo JWT refresh token với thời hạn dài hạn"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(32),
        "type": "refresh"  # Loại token
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    """Xác minh JWT token và trả về payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Kiểm tra loại token
        if payload.get("type") != token_type:
            return None
            
        return payload
    except JWTError:
        return None

def refresh_access_token(refresh_token: str, db: Session):
    """Tạo access token mới từ refresh token hợp lệ"""
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        return None
        
    username = payload.get("sub")
    if not username:
        return None
        
    # Xác minh người dùng vẫn tồn tại và đang hoạt động
    user = db.query(User).filter(User.username == username, User.is_active).first()
    if not user:
        return None
        
    # Tạo access token mới
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    # Ghi log sự kiện bảo mật
    log_security_event(
        action="token_refresh",
        user_id=user.id,
        success=True,
        details={"username": user.username}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

def authenticate_user(db: Session, username: str, password: str):
    """Xác thực người dùng với username và mật khẩu"""
    user = db.query(User).filter(User.username == username, User.is_active).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def get_current_user_from_token(token: str, db: Session):
    """Lấy thông tin user từ JWT access token"""
    payload = verify_token(token, "access")
    if not payload:
        return None
        
    username: str = payload.get("sub")
    if username is None:
        return None
        
    user = db.query(User).filter(User.username == username, User.is_active).first()
    return user

def login_user(db: Session, username: str, password: str):
    """Quy trình đăng nhập hoàn chỉnh với access + refresh tokens"""
    user = authenticate_user(db, username, password)
    if not user:
        # Ghi log thất bại
        log_security_event(
            action="login_failed",
            success=False,
            details={"username": username, "reason": "invalid_credentials"}
        )
        return None
        
    # Cập nhật lần đăng nhập cuối
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Tạo tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    # Ghi log thành công
    log_security_event(
        action="login_success",
        user_id=user.id,
        success=True,
        details={"username": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }

def create_user(db: Session, username: str, password: str, full_name: str, role: str, phone: str = None, email: str = None):
    """Tạo người dùng mới trong hệ thống"""
    # Kiểm tra username đã tồn tại chưa
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"Tên đăng nhập '{username}' đã tồn tại trong hệ thống")
    
    # Kiểm tra vai trò hợp lệ
    if not validate_role(role):
        raise ValueError(f"Vai trò '{role}' không hợp lệ. Các vai trò có sẵn: {', '.join(ROLES.keys())}")
    
    # Tạo người dùng mới
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed_password,
        full_name=full_name,
        role=role,
        phone=phone,
        email=email,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Ghi log tạo người dùng
    log_security_event(
        action="user_created",
        user_id=new_user.id,
        success=True,
        details={"username": username, "role": role, "created_by": "system"}
    )
    
    return new_user

def get_all_users(db: Session):
    """Lấy danh sách tất cả người dùng đang hoạt động"""
    return db.query(User).filter(User.is_active).all()

def get_users_by_role(db: Session, role: str):
    """Lấy danh sách người dùng theo vai trò"""
    return db.query(User).filter(User.role == role, User.is_active).all()

def update_user(db: Session, user_id: int, **kwargs):
    """Cập nhật thông tin người dùng"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Không tìm thấy người dùng trong hệ thống")
    
    # Lưu thông tin cũ để ghi log
    old_info = {
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active
    }
    
    # Cập nhật các trường
    for key, value in kwargs.items():
        if hasattr(user, key):
            if key == "password" and value:
                setattr(user, "password_hash", get_password_hash(value))
            elif key == "role" and value:
                if not validate_role(value):
                    raise ValueError(f"Vai trò '{value}' không hợp lệ")
                setattr(user, key, value)
            else:
                setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Ghi log cập nhật
    log_security_event(
        action="user_updated",
        user_id=user.id,
        success=True,
        details={
            "updated_fields": list(kwargs.keys()),
            "old_role": old_info["role"],
            "new_role": user.role
        }
    )
    
    return user

def deactivate_user(db: Session, user_id: int):
    """Vô hiệu hóa tài khoản người dùng"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Không tìm thấy người dùng trong hệ thống")
    
    if not user.is_active:
        raise ValueError("Tài khoản người dùng đã bị vô hiệu hóa trước đó")
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Ghi log vô hiệu hóa
    log_security_event(
        action="user_deactivated",
        user_id=user.id,
        success=True,
        details={"username": user.username, "reason": "admin_action"}
    )
    
    return user

# Các vai trò hệ thống - Việt hóa hoàn toàn
ROLES = {
    "assistant": "Trợ lý",
    "manager": "Quản lý", 
    "owner": "Chủ sở hữu",
    "admin": "Quản trị viên",
    "user": "Người dùng"
}

def get_role_display_name(role: str) -> str:
    """Lấy tên hiển thị tiếng Việt của vai trò"""
    return ROLES.get(role, role)

def get_available_roles() -> dict:
    """Lấy danh sách tất cả vai trò có sẵn"""
    return ROLES.copy()

def validate_role(role: str) -> bool:
    """Kiểm tra vai trò có hợp lệ không"""
    return role in ROLES.keys()