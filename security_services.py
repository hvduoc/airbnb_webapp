#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Enhanced Security Services
Dịch vụ bảo mật nâng cao cho Production Deployment
Bao gồm: Rate Limiting, Input Validation, Security Headers, CSRF Protection
Author: AI Assistant
Created: 2024-12-28
"""

import hashlib
import logging
import re
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ==================== RATE LIMITING ====================

class RateLimiter:
    """Rate Limiter với sliding window algorithm"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}  # IP -> (block_time, attempts)
    
    def is_allowed(self, identifier: str, max_requests: int, window_seconds: int, block_duration: int = 300) -> bool:
        """Kiểm tra request có được phép không"""
        current_time = time.time()
        
        # Kiểm tra IP có bị block không
        if identifier in self.blocked_ips:
            block_time, attempts = self.blocked_ips[identifier]
            if current_time - block_time < block_duration:
                logger.warning(f"🚫 IP {identifier} vẫn bị block (còn {block_duration - (current_time - block_time):.0f}s)")
                return False
            else:
                # Hết thời gian block, reset
                del self.blocked_ips[identifier]
        
        # Làm sạch requests cũ
        request_times = self.requests[identifier]
        while request_times and request_times[0] <= current_time - window_seconds:
            request_times.popleft()
        
        # Kiểm tra số lượng requests
        if len(request_times) >= max_requests:
            # Block IP nếu vượt quá giới hạn
            self.blocked_ips[identifier] = (current_time, len(request_times))
            logger.warning(f"🚫 Block IP {identifier} do vượt rate limit: {len(request_times)}/{max_requests}")
            return False
        
        # Thêm request hiện tại
        request_times.append(current_time)
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware Rate Limiting cho FastAPI"""
    
    def __init__(self, app, rate_limiter: RateLimiter, requests_per_minute: int = 100):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.requests_per_minute = requests_per_minute
        
        # Special limits cho các endpoints nhạy cảm
        self.endpoint_limits = {
            "/login": (5, 300),  # 5 requests per 5 minutes
            "/register": (3, 600),  # 3 requests per 10 minutes
            "/api/upload": (10, 60),  # 10 uploads per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        """Xử lý rate limiting cho mỗi request"""
        client_ip = self._get_client_ip(request)
        path = request.url.path
        
        # Áp dụng limit đặc biệt cho endpoint nhạy cảm
        if path in self.endpoint_limits:
            max_requests, window = self.endpoint_limits[path]
            identifier = f"{client_ip}:{path}"
        else:
            max_requests, window = self.requests_per_minute, 60
            identifier = client_ip
        
        # Kiểm tra rate limit
        if not self.rate_limiter.is_allowed(identifier, max_requests, window):
            logger.warning(f"🚫 Rate limit exceeded: {client_ip} -> {path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Quá nhiều requests",
                    "message": "Vui lòng thử lại sau vài phút",
                    "retry_after": window
                }
            )
        
        response = await call_next(request)
        
        # Thêm headers về rate limiting
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Window"] = str(window)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Lấy IP thực của client qua proxy"""
        # Kiểm tra headers từ reverse proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host

# ==================== INPUT VALIDATION ====================

class InputValidator:
    """Validator cho input security"""
    
    # Regex patterns cho validation
    PATTERNS = {
        "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        "phone": re.compile(r'^[\+]?[0-9]{10,15}$'),
        "username": re.compile(r'^[a-zA-Z0-9_]{3,20}$'),
        "property_code": re.compile(r'^[A-Z0-9-]{3,10}$'),
        "confirmation_code": re.compile(r'^[A-Z0-9]{6,20}$'),
    }
    
    # Danh sách từ khóa nguy hiểm (SQL injection, XSS)
    DANGEROUS_KEYWORDS = [
        'script', 'javascript', 'onload', 'onerror', 'alert',
        'drop table', 'delete from', 'insert into', 'update set',
        'union select', 'or 1=1', 'and 1=1', '--', '/*', '*/',
        '<script', '</script>', '<iframe', '<object', '<embed'
    ]
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 255:
            return False
        return bool(cls.PATTERNS["email"].match(email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number"""
        if not phone:
            return True  # Phone is optional
        return bool(cls.PATTERNS["phone"].match(phone))
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        return bool(cls.PATTERNS["username"].match(username))
    
    @classmethod
    def validate_password(cls, password: str, min_length: int = 8) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            "valid": True,
            "errors": [],
            "strength": "weak"
        }
        
        if not password:
            result["valid"] = False
            result["errors"].append("Mật khẩu không được để trống")
            return result
        
        if len(password) < min_length:
            result["valid"] = False
            result["errors"].append(f"Mật khẩu phải có ít nhất {min_length} ký tự")
        
        # Kiểm tra strength
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score < 2:
            result["strength"] = "weak"
            result["errors"].append("Mật khẩu quá yếu - cần có chữ hoa, chữ thường, số hoặc ký tự đặc biệt")
        elif strength_score < 3:
            result["strength"] = "medium"
        else:
            result["strength"] = "strong"
        
        return result
    
    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Sanitize input để tránh XSS và SQL injection"""
        if not text:
            return ""
        
        # Loại bỏ các ký tự HTML nguy hiểm
        text = re.sub(r'<[^>]*>', '', text)
        
        # Kiểm tra các từ khóa nguy hiểm
        text_lower = text.lower()
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"🚨 Phát hiện từ khóa nguy hiểm: {keyword}")
                text = text.replace(keyword, '***')
        
        return text.strip()
    
    @classmethod
    def validate_file_upload(cls, filename: str, content_type: str, allowed_extensions: List[str]) -> Dict[str, Any]:
        """Validate file upload"""
        result = {
            "valid": True,
            "errors": []
        }
        
        if not filename:
            result["valid"] = False
            result["errors"].append("Tên file không hợp lệ")
            return result
        
        # Kiểm tra extension
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in allowed_extensions:
            result["valid"] = False
            result["errors"].append(f"File extension '{file_ext}' không được phép. Cho phép: {', '.join(allowed_extensions)}")
        
        # Kiểm tra tên file có ký tự nguy hiểm
        dangerous_chars = ['..', '/', '\\', '<', '>', '|', ':', '*', '?', '"']
        for char in dangerous_chars:
            if char in filename:
                result["valid"] = False
                result["errors"].append("Tên file chứa ký tự không hợp lệ")
                break
        
        return result

# ==================== SECURITY HEADERS ====================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware thêm security headers"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Security headers configuration
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Thêm security headers vào response"""
        response = await call_next(request)
        
        # Thêm tất cả security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Server header để ẩn thông tin server
        response.headers["Server"] = "Airbnb-WebApp"
        
        return response

# ==================== CSRF PROTECTION ====================

class CSRFProtection:
    """CSRF Protection system"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.token_expiry = 3600  # 1 hour
    
    def generate_token(self, session_id: str) -> str:
        """Tạo CSRF token cho session"""
        timestamp = str(int(time.time()))
        data = f"{session_id}:{timestamp}"
        signature = hashlib.sha256(f"{data}:{self.secret_key}".encode()).hexdigest()
        token = f"{timestamp}.{signature}"
        return token
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        try:
            if not token or '.' not in token:
                return False
            
            timestamp_str, signature = token.split('.', 1)
            timestamp = int(timestamp_str)
            
            # Kiểm tra expiry
            if time.time() - timestamp > self.token_expiry:
                logger.warning(f"🚨 CSRF token expired: {token}")
                return False
            
            # Verify signature
            data = f"{session_id}:{timestamp_str}"
            expected_signature = hashlib.sha256(f"{data}:{self.secret_key}".encode()).hexdigest()
            
            if signature != expected_signature:
                logger.warning(f"🚨 Invalid CSRF token signature: {token}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"🚨 CSRF token validation error: {e}")
            return False

# ==================== PASSWORD POLICY ====================

class PasswordPolicy:
    """Password policy enforcement"""
    
    def __init__(self):
        self.min_length = 8
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.common_passwords = self._load_common_passwords()
    
    def _load_common_passwords(self) -> set:
        """Load danh sách mật khẩu phổ biến"""
        return {
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey",
            "1234567890", "dragon", "master", "hello", "freedom"
        }
    
    def validate_password(self, password: str, username: str = None) -> Dict[str, Any]:
        """Comprehensive password validation"""
        result = {
            "valid": True,
            "errors": [],
            "strength_score": 0,
            "suggestions": []
        }
        
        if not password:
            result["valid"] = False
            result["errors"].append("Mật khẩu không được để trống")
            return result
        
        # Length check
        if len(password) < self.min_length:
            result["valid"] = False
            result["errors"].append(f"Mật khẩu phải có ít nhất {self.min_length} ký tự")
        
        if len(password) > self.max_length:
            result["valid"] = False
            result["errors"].append(f"Mật khẩu không được dài quá {self.max_length} ký tự")
        
        # Character requirements
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if self.require_uppercase and not has_upper:
            result["valid"] = False
            result["errors"].append("Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa")
        
        if self.require_lowercase and not has_lower:
            result["valid"] = False
            result["errors"].append("Mật khẩu phải chứa ít nhất 1 chữ cái viết thường")
        
        if self.require_digits and not has_digit:
            result["valid"] = False
            result["errors"].append("Mật khẩu phải chứa ít nhất 1 chữ số")
        
        if self.require_special and not has_special:
            result["valid"] = False
            result["errors"].append("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (!@#$%^&*)")
        
        # Common password check
        if password.lower() in self.common_passwords:
            result["valid"] = False
            result["errors"].append("Mật khẩu này quá phổ biến và không an toàn")
        
        # Username similarity check
        if username and len(username) > 3 and username.lower() in password.lower():
            result["valid"] = False
            result["errors"].append("Mật khẩu không được chứa tên đăng nhập")
        
        # Calculate strength score
        strength_factors = [has_upper, has_lower, has_digit, has_special]
        result["strength_score"] = sum(strength_factors) * 25  # 0-100 scale
        
        # Length bonus
        if len(password) >= 12:
            result["strength_score"] += 10
        if len(password) >= 16:
            result["strength_score"] += 10
        
        # Suggestions
        if not has_upper:
            result["suggestions"].append("Thêm chữ cái viết hoa")
        if not has_lower:
            result["suggestions"].append("Thêm chữ cái viết thường")
        if not has_digit:
            result["suggestions"].append("Thêm chữ số")
        if not has_special:
            result["suggestions"].append("Thêm ký tự đặc biệt")
        if len(password) < 12:
            result["suggestions"].append("Tăng độ dài lên ít nhất 12 ký tự")
        
        return result

# ==================== SECURITY AUDIT LOG ====================

class SecurityAuditLogger:
    """Security event logging system"""
    
    def __init__(self):
        self.logger = logging.getLogger("security_audit")
        
        # Tạo file handler riêng cho security logs
        handler = logging.FileHandler("logs/security_audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log security event"""
        {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details,
            "severity": severity
        }
        
        if severity == "CRITICAL":
            self.logger.critical(f"🚨 {event_type}: {details}")
        elif severity == "WARNING":
            self.logger.warning(f"⚠️ {event_type}: {details}")
        else:
            self.logger.info(f"ℹ️ {event_type}: {details}")
    
    def log_failed_login(self, username: str, ip_address: str, reason: str):
        """Log failed login attempt"""
        self.log_event(
            "FAILED_LOGIN",
            {
                "username": username,
                "ip_address": ip_address,
                "reason": reason
            },
            "WARNING"
        )
    
    def log_suspicious_activity(self, activity: str, ip_address: str, details: Dict[str, Any]):
        """Log suspicious activity"""
        self.log_event(
            "SUSPICIOUS_ACTIVITY",
            {
                "activity": activity,
                "ip_address": ip_address,
                **details
            },
            "CRITICAL"
        )

# Global instances
rate_limiter = RateLimiter()
input_validator = InputValidator()
password_policy = PasswordPolicy()
security_audit_logger = SecurityAuditLogger()

# Export cho sử dụng trong app
__all__ = [
    "RateLimiter", "RateLimitMiddleware", "InputValidator", 
    "SecurityHeadersMiddleware", "CSRFProtection", "PasswordPolicy",
    "SecurityAuditLogger", "rate_limiter", "input_validator",
    "password_policy", "security_audit_logger"
]