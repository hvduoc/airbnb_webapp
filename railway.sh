#!/bin/bash

# Railway Startup Script for Airbnb WebApp

echo "🚀 Starting Airbnb WebApp on Railway..."

# Run database migrations
echo "📋 Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec python payment_production.py