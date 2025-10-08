"""
Cấu hình môi trường cho deployment
"""

import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment_ledger.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "airbnb-payment-ledger-production-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# File Upload
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Production settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Cookie settings
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "True").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

print(f"✅ Environment: {ENVIRONMENT}")
print(f"✅ Debug mode: {DEBUG}")
print(f"✅ Database: {DATABASE_URL}")
print(f"✅ Cookie secure: {COOKIE_SECURE}")
