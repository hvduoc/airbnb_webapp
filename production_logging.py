#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Production Logging System
Hệ thống logging structured cho Production với JSON format
Tích hợp ELK Stack, Error tracking, Performance monitoring
Author: AI Assistant  
Created: 2024-12-28
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
import sys
from contextlib import contextmanager

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter cho structured logging"""
    
    def format(self, record):
        """Format log record thành JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Thêm thông tin request nếu có
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'ip_address'):
            log_entry["ip_address"] = record.ip_address
        
        # Thêm exception info nếu có
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Thêm extra data nếu có
        if hasattr(record, 'extra_data'):
            log_entry["extra"] = record.extra_data
        
        return json.dumps(log_entry, ensure_ascii=False)

class SecurityLogFormatter(JSONFormatter):
    """Specialized formatter cho security events"""
    
    def format(self, record):
        """Format security log với enhanced fields"""
        log_entry = json.loads(super().format(record))
        
        # Thêm security-specific fields
        log_entry["event_category"] = "security"
        log_entry["severity"] = getattr(record, 'severity', 'INFO')
        log_entry["event_type"] = getattr(record, 'event_type', 'unknown')
        
        if hasattr(record, 'threat_level'):
            log_entry["threat_level"] = record.threat_level
        
        return json.dumps(log_entry, ensure_ascii=False)

class PerformanceLogFormatter(JSONFormatter):
    """Specialized formatter cho performance metrics"""
    
    def format(self, record):
        """Format performance log với metrics"""
        log_entry = json.loads(super().format(record))
        
        # Performance-specific fields
        log_entry["event_category"] = "performance"
        
        if hasattr(record, 'duration'):
            log_entry["duration_ms"] = record.duration
        
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        if hasattr(record, 'memory_usage'):
            log_entry["memory_mb"] = record.memory_usage
        
        return json.dumps(log_entry, ensure_ascii=False)

class AirbnbProductionLogger:
    """Centralized logging system cho Airbnb WebApp Production"""
    
    def __init__(self, app_name: str = "airbnb-webapp"):
        self.app_name = app_name
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        
        # Tạo logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler với color coding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Application log file handler
        app_handler = logging.handlers.RotatingFileHandler(
            "logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(app_handler)
        
        # Error log file handler
        error_handler = logging.handlers.RotatingFileHandler(
            "logs/error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
        
        # Security log handler
        security_logger = logging.getLogger("security")
        security_handler = logging.handlers.RotatingFileHandler(
            "logs/security.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(SecurityLogFormatter())
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
        security_logger.propagate = False  # Không propagate lên root logger
        
        # Performance log handler
        performance_logger = logging.getLogger("performance")
        performance_handler = logging.handlers.RotatingFileHandler(
            "logs/performance.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(PerformanceLogFormatter())
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.INFO)
        performance_logger.propagate = False
        
        # Access log handler (cho HTTP requests)
        access_logger = logging.getLogger("access")
        access_handler = logging.handlers.RotatingFileHandler(
            "logs/access.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(JSONFormatter())
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
    
    def get_logger(self, name: str) -> logging.Logger:
        """Lấy logger với tên cụ thể"""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float, 
                   user_id: Optional[int] = None, ip_address: Optional[str] = None):
        """Log HTTP request"""
        access_logger = logging.getLogger("access")
        
        extra = {
            'extra_data': {
                'method': method,
                'path': path,
                'status_code': status_code,
                'duration_ms': duration_ms,
                'user_id': user_id,
                'ip_address': ip_address
            }
        }
        
        if status_code >= 400:
            access_logger.error(f"HTTP {status_code} - {method} {path}", extra=extra)
        else:
            access_logger.info(f"HTTP {status_code} - {method} {path}", extra=extra)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          severity: str = "INFO", threat_level: str = "LOW"):
        """Log security event"""
        security_logger = logging.getLogger("security")
        
        extra = {
            'event_type': event_type,
            'severity': severity,
            'threat_level': threat_level,
            'extra_data': details
        }
        
        if severity == "CRITICAL":
            security_logger.critical(f"Security Event: {event_type}", extra=extra)
        elif severity == "WARNING":
            security_logger.warning(f"Security Event: {event_type}", extra=extra)
        else:
            security_logger.info(f"Security Event: {event_type}", extra=extra)
    
    def log_performance(self, operation: str, duration_ms: float, 
                       endpoint: Optional[str] = None, memory_mb: Optional[float] = None):
        """Log performance metrics"""
        performance_logger = logging.getLogger("performance")
        
        extra = {
            'duration': duration_ms,
            'endpoint': endpoint,
            'memory_usage': memory_mb,
            'extra_data': {
                'operation': operation
            }
        }
        
        if duration_ms > 1000:  # Slow operation > 1s
            performance_logger.warning(f"Slow operation: {operation} ({duration_ms}ms)", extra=extra)
        else:
            performance_logger.info(f"Performance: {operation} ({duration_ms}ms)", extra=extra)
    
    def log_database_query(self, query: str, duration_ms: float, rows_affected: int = 0):
        """Log database query performance"""
        db_logger = self.get_logger("database")
        
        extra = {
            'extra_data': {
                'query_type': query.split()[0].upper() if query else 'UNKNOWN',
                'duration_ms': duration_ms,
                'rows_affected': rows_affected,
                'query': query[:200] + "..." if len(query) > 200 else query
            }
        }
        
        if duration_ms > 500:  # Slow query > 500ms
            db_logger.warning(f"Slow database query ({duration_ms}ms)", extra=extra)
        else:
            db_logger.info(f"Database query ({duration_ms}ms)", extra=extra)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error với full context"""
        error_logger = self.get_logger("error")
        
        extra = {
            'extra_data': {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context or {}
            }
        }
        
        error_logger.error(f"Application Error: {str(error)}", exc_info=True, extra=extra)
    
    def log_user_action(self, action: str, user_id: int, details: Dict[str, Any]):
        """Log user action cho audit trail"""
        audit_logger = self.get_logger("audit")
        
        extra = {
            'user_id': user_id,
            'extra_data': {
                'action': action,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        audit_logger.info(f"User Action: {action}", extra=extra)

@contextmanager
def log_performance_context(logger: AirbnbProductionLogger, operation: str, endpoint: Optional[str] = None):
    """Context manager để log performance tự động"""
    import time
    
    start_time = time.time()
    
    try:
        yield
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        logger.log_performance(
            operation=operation,
            duration_ms=duration_ms,
            endpoint=endpoint
        )

# Khởi tạo global logger instance cho production
production_logger = AirbnbProductionLogger()

# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message"""
    logger = production_logger.get_logger("app")
    logger.info(message, extra={'extra_data': kwargs} if kwargs else None)

def log_warning(message: str, **kwargs):
    """Log warning message"""
    logger = production_logger.get_logger("app")
    logger.warning(message, extra={'extra_data': kwargs} if kwargs else None)

def log_error(message: str, error: Optional[Exception] = None, **kwargs):
    """Log error message"""
    logger = production_logger.get_logger("app")
    if error:
        production_logger.log_error(error, kwargs)
    else:
        logger.error(message, extra={'extra_data': kwargs} if kwargs else None)

def log_debug(message: str, **kwargs):
    """Log debug message"""
    logger = production_logger.get_logger("app")
    logger.debug(message, extra={'extra_data': kwargs} if kwargs else None)

def log_security_event(action: str, user_id: Optional[int] = None, success: bool = True, details: Dict[str, Any] = None):
    """Log security event - tương thích với auth_service.py"""
    severity = "INFO" if success else "WARNING"
    threat_level = "LOW" if success else "MEDIUM"
    
    event_details = {
        "action": action,
        "user_id": user_id,
        "success": success,
        "details": details or {}
    }
    
    production_logger.log_security_event(
        event_type=action,
        details=event_details,
        severity=severity,
        threat_level=threat_level
    )

# Export
__all__ = [
    "AirbnbProductionLogger", "JSONFormatter", "SecurityLogFormatter", "PerformanceLogFormatter",
    "log_performance_context", "production_logger",
    "log_info", "log_warning", "log_error", "log_debug", "log_security_event"
]