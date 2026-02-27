#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Change to the directory where the script is located (project root)
cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 Launching Autonomous Content Factory"
echo "=========================================="

# Check for GEMINI_API_KEY in environment or .env file
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "Loading GEMINI_API_KEY from .env file..."
        export $(grep -v '^#' .env | xargs)
    fi
    
    if [ -z "$GEMINI_API_KEY" ]; then
        echo "❌ ERROR: GEMINI_API_KEY is not set in your environment or .env file."
        echo "Please export it or create a .env file with GEMINI_API_KEY=your_key"
        exit 1
    fi
fi

# 1. Check and start Redis
echo "Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis is not running. Attempting to start Redis server..."
    # Attempt to start redis in the background
    redis-server --daemonize yes || {
        echo "Failed to start Redis. Please start it manually (e.g., 'sudo systemctl start redis-server')."
        exit 1
    }
    sleep 2
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "Redis is still not responding. Exiting..."
        exit 1
    fi
    echo "Redis started successfully."
else
    echo "✅ Redis is already running."
fi

# 2. Check and start Celery Worker
echo "Checking Celery worker..."
if pgrep -f "celery -A config worker" > /dev/null; then
    echo "Stopping existing Celery worker..."
    pkill -f "celery -A config worker" || true
    sleep 2
fi

echo "Starting Celery worker..."
nohup uv run celery -A config worker -l INFO > celery.log 2>&1 &
echo "✅ Celery started (PID: $!). Background logs at celery.log"

# 3. Check and start Django Server
echo "Checking Django development server..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Stopping existing Django development server on port 8000..."
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t) || true
    sleep 2
fi

echo "Starting Django development server..."
nohup uv run python manage.py runserver > django.log 2>&1 &
echo "✅ Django started (PID: $!). Background logs at django.log"
sleep 2 # wait a moment for it to start

echo "=========================================="
echo "🎉 All services are up and running!"
echo "👉 Access the app at: http://127.0.0.1:8000/"
echo "=========================================="
