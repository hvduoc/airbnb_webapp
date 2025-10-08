# ================================================================
# AIRBNB WEBAPP - Production Dockerfile
# Multi-stage Docker build cho Python FastAPI application
# Optimized cho production với security và performance
# Author: AI Assistant
# Created: 2024-12-28
# ================================================================

# ==================== BUILD STAGE ====================
FROM python:3.10-slim as builder

# Metadata
LABEL maintainer="Airbnb Vietnam WebApp Team"
LABEL description="Airbnb WebApp Production Container"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Cài đặt system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Tạo virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements và install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ==================== PRODUCTION STAGE ====================
FROM python:3.10-slim as production

# Metadata cho production stage
LABEL stage="production"

# Set environment variables cho production
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PATH="/opt/venv/bin:$PATH"

# Cài đặt runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Tạo non-root user cho security
RUN groupadd -r airbnb && \
    useradd -r -g airbnb -d /app -s /bin/bash airbnb && \
    mkdir -p /app /app/logs /app/uploads /app/backups && \
    chown -R airbnb:airbnb /app

# Copy virtual environment từ builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=airbnb:airbnb . .

# Tạo thư mục cần thiết với proper permissions
RUN mkdir -p logs uploads backups static templates && \
    chown -R airbnb:airbnb logs uploads backups static templates && \
    chmod 755 logs uploads backups static templates

# Switch to non-root user
USER airbnb

# Expose port
EXPOSE 8000
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - sử dụng main.py thay vì payment_production.py
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4"]

# ==================== DEVELOPMENT STAGE ====================
FROM production as development

# Metadata cho development stage
LABEL stage="development"

# Set environment variables cho development
ENV ENVIRONMENT=development \
    DEBUG=true \
    RELOAD=true

# Switch back to root để install dev dependencies
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN /opt/venv/bin/pip install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython \
    jupyter

# Switch back to airbnb user
USER airbnb

# Development command với hot reload
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]