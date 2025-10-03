"""
Simple Rate Limiting for Airbnb WebApp
In-memory rate limiting with sliding window algorithm
"""
import threading
import time
from collections import defaultdict, deque
from typing import Dict, Optional

from fastapi import HTTPException, Request, status


class RateLimiter:
    """Simple in-memory rate limiter using sliding window"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = threading.Lock()
    
    def _get_client_key(self, request: Request) -> str:
        """Generate client identifier for rate limiting"""
        # Use IP address as primary identifier
        ip = request.client.host if request.client else "unknown"
        
        # Add user ID if authenticated for more granular limiting
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        return f"ip:{ip}"
    
    def _cleanup_old_requests(self, request_times: deque):
        """Remove requests outside the current window"""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
    
    def is_allowed(self, request: Request) -> bool:
        """Check if request is allowed based on rate limits"""
        client_key = self._get_client_key(request)
        current_time = time.time()
        
        with self.lock:
            request_times = self.requests[client_key]
            
            # Clean up old requests
            self._cleanup_old_requests(request_times)
            
            # Check if under limit
            if len(request_times) >= self.max_requests:
                return False
            
            # Add current request
            request_times.append(current_time)
            return True
    
    def get_remaining_requests(self, request: Request) -> int:
        """Get number of remaining requests for client"""
        client_key = self._get_client_key(request)
        
        with self.lock:
            request_times = self.requests[client_key]
            self._cleanup_old_requests(request_times)
            return max(0, self.max_requests - len(request_times))
    
    def get_reset_time(self, request: Request) -> Optional[float]:
        """Get time when rate limit resets for client"""
        client_key = self._get_client_key(request)
        
        with self.lock:
            request_times = self.requests[client_key]
            if not request_times:
                return None
            
            return request_times[0] + self.window_seconds

# Global rate limiter instances
api_rate_limiter = None
auth_rate_limiter = None

def init_rate_limiters(api_limit: int = 100, auth_limit: int = 10):
    """Initialize rate limiters"""
    global api_rate_limiter, auth_rate_limiter
    
    # General API rate limiter
    api_rate_limiter = RateLimiter(
        max_requests=api_limit,
        window_seconds=60  # 1 minute window
    )
    
    # Stricter rate limiter for authentication endpoints
    auth_rate_limiter = RateLimiter(
        max_requests=auth_limit,
        window_seconds=60  # 1 minute window
    )

def check_rate_limit(request: Request, limiter_type: str = "api") -> bool:
    """Check rate limit for request"""
    limiter = api_rate_limiter if limiter_type == "api" else auth_rate_limiter
    
    if not limiter:
        return True  # No rate limiting if not initialized
    
    return limiter.is_allowed(request)

def get_rate_limit_headers(request: Request, limiter_type: str = "api") -> Dict[str, str]:
    """Get rate limit headers for response"""
    limiter = api_rate_limiter if limiter_type == "api" else auth_rate_limiter
    
    if not limiter:
        return {}
    
    remaining = limiter.get_remaining_requests(request)
    reset_time = limiter.get_reset_time(request)
    
    headers = {
        "X-RateLimit-Limit": str(limiter.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Window": str(limiter.window_seconds)
    }
    
    if reset_time:
        headers["X-RateLimit-Reset"] = str(int(reset_time))
    
    return headers

def rate_limit_exceeded_response():
    """Standard response for rate limit exceeded"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": 60
        },
        headers={"Retry-After": "60"}
    )