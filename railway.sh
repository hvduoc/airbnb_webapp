#!/bin/bash

# Railway Startup Script
echo "🚀 Starting Airbnb WebApp..."

# Set environment
export PYTHONUNBUFFERED=1

# Run migrations only if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
    echo "📋 Running database migrations..."
    alembic upgrade head
else
    echo "⚠️ No DATABASE_URL set, skipping migrations"
fi

# Start app
echo "🌐 Starting server on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}