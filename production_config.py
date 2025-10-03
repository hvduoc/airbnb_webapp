#!/usr/bin/env python3
"""
AIRBNB WEBAPP - Configuration Management System
Quản lý cấu hình môi trường cho tất cả các giai đoạn triển khai
Hỗ trợ Development, Staging, Production với bảo mật cao cấp
Author: AI Assistant
Created: 2024-12-28
"""

import logging
import os
import secrets
from enum import Enum
from typing import List, Optional

from pydantic import validator
from pydantic_settings import BaseSettings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Các môi trường triển khai được hỗ trợ"""
    DEVELOPMENT = "development"
    STAGING = "staging"  
    PRODUCTION = "production"

class BaseConfig(BaseSettings):
    """Cấu hình cơ bản cho tất cả môi trường"""
    
    # ==================== GENERAL ====================
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    APP_NAME: str = "Airbnb Vietnam WebApp"
    APP_VERSION: str = "1.0.0"
    APP_URL: str = "http://localhost:8000"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # ==================== SECURITY ====================
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    
    # Enhanced Security
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION: int = 300  # 5 minutes
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_STRONG_PASSWORD: bool = True
    
    # ==================== DATABASE ====================
    DATABASE_TYPE: str = "sqlite"
    
    # SQLite Configuration
    SQLITE_DATABASE_URL: str = "sqlite:///./app.db"
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "airbnb_webapp"
    POSTGRES_USER: str = "airbnb_user"
    POSTGRES_PASSWORD: str = "secure_password"
    POSTGRES_SSL_MODE: str = "prefer"
    
    # Connection Pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # ==================== REDIS ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    
    # Session Configuration
    SESSION_TIMEOUT: int = 3600
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_FILE_MAX_SIZE: int = 10485760  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # External Logging
    ELASTICSEARCH_HOST: Optional[str] = None
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_INDEX: str = "airbnb-webapp-logs"
    
    # ==================== MONITORING ====================
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_ENDPOINT: str = "/metrics"
    
    # ==================== EMAIL ====================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    FROM_EMAIL: str = "noreply@airbnb-webapp.com"
    SUPPORT_EMAIL: str = "support@airbnb-webapp.com"
    
    # ==================== FILE UPLOAD ====================
    UPLOAD_FOLDER: str = "uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf", "csv"]
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    LOGIN_RATE_LIMIT: int = 5
    LOGIN_RATE_PERIOD: int = 300
    
    # ==================== CORS ====================
    CORS_ENABLED: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["Content-Type", "Authorization"]
    
    # ==================== SSL/TLS ====================
    SSL_ENABLED: bool = False
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    SSL_CA_PATH: Optional[str] = None
    
    # ==================== BACKUP ====================
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_STORAGE_PATH: str = "/backups"
    BACKUP_COMPRESSION: bool = True
    BACKUP_TO_S3: bool = False
    BACKUP_S3_BUCKET: Optional[str] = None
    
    # ==================== FEATURE FLAGS ====================
    ENABLE_USER_REGISTRATION: bool = True
    ENABLE_CSV_UPLOAD: bool = True
    ENABLE_EXPENSE_TRACKING: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_API_DOCS: bool = True
    MAINTENANCE_MODE: bool = False
    MAINTENANCE_MESSAGE: str = "Hệ thống đang bảo trì. Vui lòng thử lại sau."
    
    # ==================== LOCALIZATION ====================
    DEFAULT_LANGUAGE: str = "vi"
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    CURRENCY: str = "VND"
    DATE_FORMAT: str = "%d/%m/%Y"
    TIME_FORMAT: str = "%H:%M:%S"
    
    # ==================== DEVELOPMENT ====================
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_PROFILER: bool = False
    ENABLE_MOCK_DATA: bool = False
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    @validator("SECRET_KEY", pre=True, always=True)
    def generate_secret_key(cls, v):
        """Tự động tạo SECRET_KEY nếu không được cung cấp"""
        if not v:
            v = secrets.token_urlsafe(64)
            logger.warning("🔐 SECRET_KEY được tạo tự động. Hãy lưu vào environment:")
            logger.warning(f"export SECRET_KEY='{v}'")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins từ string hoặc list"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    @validator("CORS_METHODS", pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods từ string hoặc list"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    @validator("CORS_HEADERS", pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers từ string hoặc list"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        """Parse allowed extensions từ string hoặc list"""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    def get_database_url(self) -> str:
        """Lấy database URL dựa trên cấu hình"""
        if self.DATABASE_TYPE == "postgresql":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?sslmode={self.POSTGRES_SSL_MODE}"
        else:
            return self.SQLITE_DATABASE_URL
    
    def get_redis_url(self) -> str:
        """Lấy Redis URL với authentication nếu có"""
        scheme = "rediss" if self.REDIS_SSL else "redis"
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"{scheme}://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def is_development(self) -> bool:
        """Kiểm tra có phải môi trường development không"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Kiểm tra có phải môi trường production không"""
        return self.ENVIRONMENT == Environment.PRODUCTION

class DevelopmentConfig(BaseConfig):
    """Cấu hình cho môi trường Development"""
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENABLE_DEBUG_TOOLBAR: bool = True
    ENABLE_MOCK_DATA: bool = True
    SESSION_COOKIE_SECURE: bool = False
    SSL_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = False  # Tắt rate limiting trong dev

class StagingConfig(BaseConfig):
    """Cấu hình cho môi trường Staging"""
    ENVIRONMENT: Environment = Environment.STAGING
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_TYPE: str = "postgresql"
    SESSION_COOKIE_SECURE: bool = True
    SSL_ENABLED: bool = True
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_MOCK_DATA: bool = False
    
    # Cấu hình bảo mật cao hơn cho staging
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    MAX_LOGIN_ATTEMPTS: int = 3
    BCRYPT_ROUNDS: int = 14

class ProductionConfig(BaseConfig):
    """Cấu hình cho môi trường Production"""
    ENVIRONMENT: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "WARNING"
    DATABASE_TYPE: str = "postgresql"
    POSTGRES_SSL_MODE: str = "require"
    SESSION_COOKIE_SECURE: bool = True
    SSL_ENABLED: bool = True
    REDIS_SSL: bool = True
    
    # Security hardening cho production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    MAX_LOGIN_ATTEMPTS: int = 3
    ACCOUNT_LOCKOUT_DURATION: int = 600  # 10 minutes
    BCRYPT_ROUNDS: int = 15
    
    # Tắt các tính năng development
    ENABLE_DEBUG_TOOLBAR: bool = False
    ENABLE_PROFILER: bool = False
    ENABLE_MOCK_DATA: bool = False
    ENABLE_API_DOCS: bool = False  # Tắt API docs trong production
    
    # Enhanced monitoring cho production
    ENABLE_METRICS: bool = True
    PROMETHEUS_ENABLED: bool = True

def get_config() -> BaseConfig:
    """Factory function để lấy config dựa trên environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    config = config_class()
    
    # Log thông tin môi trường
    logger.info(f"🚀 Khởi tạo cấu hình cho môi trường: {config.ENVIRONMENT.value}")
    logger.info(f"📊 Database: {config.DATABASE_TYPE}")
    logger.info(f"🔒 SSL: {'Enabled' if config.SSL_ENABLED else 'Disabled'}")
    logger.info(f"📈 Monitoring: {'Enabled' if config.ENABLE_METRICS else 'Disabled'}")
    
    return config

def validate_production_config(config: BaseConfig) -> List[str]:
    """Validate production configuration và trả về danh sách warnings"""
    warnings = []
    
    if config.ENVIRONMENT == Environment.PRODUCTION:
        # Kiểm tra SECRET_KEY
        if len(config.SECRET_KEY) < 32:
            warnings.append("SECRET_KEY quá ngắn cho production (cần ít nhất 32 ký tự)")
        
        # Kiểm tra database
        if config.DATABASE_TYPE != "postgresql":
            warnings.append("Production nên sử dụng PostgreSQL thay vì SQLite")
        
        # Kiểm tra SSL
        if not config.SSL_ENABLED:
            warnings.append("SSL/TLS nên được kích hoạt trong production")
        
        # Kiểm tra debug mode
        if config.DEBUG:
            warnings.append("DEBUG mode nên được tắt trong production")
        
        # Kiểm tra CORS
        if "localhost" in str(config.CORS_ORIGINS):
            warnings.append("CORS origins chứa localhost - có thể không phù hợp cho production")
        
        # Kiểm tra monitoring
        if not config.ENABLE_METRICS:
            warnings.append("Monitoring nên được kích hoạt trong production")
    
    return warnings

# Global config instance
settings = get_config()

# Validate production configuration
if settings.ENVIRONMENT == Environment.PRODUCTION:
    production_warnings = validate_production_config(settings)
    if production_warnings:
        logger.warning("⚠️ CẢNH BÁO PRODUCTION CONFIGURATION:")
        for warning in production_warnings:
            logger.warning(f"   • {warning}")

# Export config cho sử dụng trong app
__all__ = ["settings", "get_config", "BaseConfig", "DevelopmentConfig", "StagingConfig", "ProductionConfig"]