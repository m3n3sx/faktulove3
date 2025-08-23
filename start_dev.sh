#!/bin/bash
# Start all development services

echo "Starting development environment..."

# Start Docker services
docker-compose up -d postgres redis

# Wait for services
sleep 5

# Activate virtual environment
source venv/bin/activate

# Start Celery worker in background
celery -A faktury_projekt worker -l info -Q ocr,cleanup &
CELERY_WORKER_PID=$!

# Start Celery beat in background
celery -A faktury_projekt beat -l info &
CELERY_BEAT_PID=$!

# Start Django development server
python manage.py runserver

# Cleanup on exit
trap "kill $CELERY_WORKER_PID $CELERY_BEAT_PID; docker-compose down" EXIT