#!/bin/bash
# Stop all development services

echo "Stopping development environment..."

# Stop Celery processes
pkill -f "celery worker"
pkill -f "celery beat"

# Stop Docker services
docker-compose down

echo "Development environment stopped"