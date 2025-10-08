"""
Logging configuration for Airbnb WebApp
Production-ready logging with structured output, rotation, and monitoring
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any, Dict


def setup_logging():
    """Setup production-grade logging configuration"""

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    # Get log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create app logger
    logger = logging.getLogger("airbnb_webapp")
    logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    log_file = os.path.join(logs_dir, "app.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Error file handler for errors only
    error_file = os.path.join(logs_dir, "errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)

    # Security audit log handler
    security_file = os.path.join(logs_dir, "security.log")
    security_handler = logging.handlers.RotatingFileHandler(
        security_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,  # Keep more security logs
        encoding="utf-8",
    )
    security_formatter = JsonFormatter()
    security_handler.setFormatter(security_formatter)

    # Create security logger
    security_logger = logging.getLogger("airbnb_webapp.security")
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)

    # Suppress external library noise in production
    if os.getenv("PRODUCTION", "false").lower() == "true":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
        if hasattr(record, "action"):
            log_entry["action"] = record.action
        if hasattr(record, "resource"):
            log_entry["resource"] = record.resource

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def log_security_event(
    action: str,
    user_id: int = None,
    ip_address: str = None,
    resource: str = None,
    success: bool = True,
    details: Dict[str, Any] = None,
):
    """Log security-related events for audit trail"""
    security_logger = logging.getLogger("airbnb_webapp.security")

    extra = {
        "action": action,
        "user_id": user_id,
        "ip_address": ip_address,
        "resource": resource,
        "success": success,
    }

    message = f"Security event: {action}"
    if not success:
        message += " (FAILED)"

    if details:
        message += f" - {details}"

    level = logging.INFO if success else logging.WARNING
    security_logger.log(level, message, extra=extra)


def log_api_access(
    request_path: str,
    method: str,
    user_id: int = None,
    ip_address: str = None,
    status_code: int = None,
    duration: float = None,
):
    """Log API access for monitoring and analytics"""
    logger = logging.getLogger("airbnb_webapp.api")

    extra = {"action": "api_access", "user_id": user_id, "ip_address": ip_address}

    message = f"{method} {request_path}"
    if status_code:
        message += f" -> {status_code}"
    if duration:
        message += f" ({duration:.2f}ms)"

    level = logging.INFO if (status_code and status_code < 400) else logging.WARNING
    logger.log(level, message, extra=extra)


# Initialize logging when module is imported
app_logger = setup_logging()
