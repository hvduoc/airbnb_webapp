"""
CSRF Protection for Airbnb WebApp
Simple but effective CSRF protection using double-submit cookies
"""
import hashlib
import hmac
import secrets
import time
from typing import Optional

from fastapi import Request, Response


class CSRFProtection:
    """CSRF protection using double-submit cookie pattern"""
    
    def __init__(self, secret_key: str, token_lifetime: int = 3600):
        self.secret_key = secret_key.encode()
        self.token_lifetime = token_lifetime  # 1 hour default
    
    def generate_token(self) -> str:
        """Generate a new CSRF token"""
        timestamp = str(int(time.time()))
        random_part = secrets.token_urlsafe(32)
        message = f"{timestamp}:{random_part}"
        
        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{message}:{signature}"
    
    def validate_token(self, token: str) -> bool:
        """Validate CSRF token"""
        if not token:
            return False
        
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            timestamp, random_part, signature = parts
            message = f"{timestamp}:{random_part}"
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False
            
            # Check if token is still valid (not expired)
            token_time = int(timestamp)
            current_time = int(time.time())
            
            if current_time - token_time > self.token_lifetime:
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract CSRF token from request (header or form)"""
        # Check X-CSRF-Token header first
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # Check form data (for regular form submissions)
        if hasattr(request, "_form"):
            form_data = request._form
            if isinstance(form_data, dict):
                return form_data.get("csrf_token")
        
        return None
    
    def validate_request(self, request: Request, response: Response) -> bool:
        """Validate CSRF token for state-changing requests"""
        # Only check for state-changing methods
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        
        # Get token from request
        token = self.get_token_from_request(request)
        
        # Get token from cookie
        cookie_token = request.cookies.get("csrf_token")
        
        # Both tokens must be present and match
        if not token or not cookie_token:
            return False
        
        if not hmac.compare_digest(token, cookie_token):
            return False
        
        # Validate token format and expiration
        return self.validate_token(token)
    
    def set_csrf_cookie(self, response: Response, token: str):
        """Set CSRF token in cookie"""
        response.set_cookie(
            key="csrf_token",
            value=token,
            max_age=self.token_lifetime,
            httponly=False,  # Needs to be accessible to JavaScript
            secure=False,  # Set to True in production with HTTPS
            samesite="strict"
        )

# Global CSRF protection instance
csrf_protection = None

def init_csrf_protection(secret_key: str):
    """Initialize CSRF protection with secret key"""
    global csrf_protection
    csrf_protection = CSRFProtection(secret_key)
    return csrf_protection

def get_csrf_token() -> str:
    """Generate a new CSRF token"""
    if not csrf_protection:
        raise RuntimeError("CSRF protection not initialized")
    return csrf_protection.generate_token()

def validate_csrf_token(request: Request, response: Response) -> bool:
    """Validate CSRF token for request"""
    if not csrf_protection:
        return True  # Skip validation if not initialized
    return csrf_protection.validate_request(request, response)

def set_csrf_token_cookie(response: Response, token: str = None):
    """Set CSRF token in response cookie"""
    if not csrf_protection:
        return
    
    if not token:
        token = get_csrf_token()
    
    csrf_protection.set_csrf_cookie(response, token)
    return token