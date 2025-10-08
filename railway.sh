#!/bin/bash

# Railway Startup Script for Airbnb WebApp

echo "🚀 Starting Airbnb WebApp on Railway..."

# Set environment variables
export PYTHONUNBUFFERED=1
export PORT=${PORT:-8000}

# Run database migrations
echo "📋 Running database migrations..."
alembic upgrade head

# Start the FastAPI application  
echo "🌐 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1