#!/bin/bash

# FaktuLove OCR - Production Deployment Script
# Automates the complete production deployment process

set -e

echo "🚀 FaktuLove OCR - Production Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}[DEPLOY]${NC} $1"
}

print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="deployment_$(date +%Y%m%d_%H%M%S).log"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Start logging
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

print_header "Starting Production Deployment for $ENVIRONMENT"

# Step 1: Pre-deployment Checks
print_header "1. Pre-deployment Validation"

print_status "Checking prerequisites..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run from Django project root."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ $(echo "$python_version < 3.8" | bc -l 2>/dev/null || echo 1) -eq 1 ]]; then
    print_error "Python 3.8+ required. Current: $python_version"
    exit 1
fi

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not active. Activating..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Please create one first."
        exit 1
    fi
fi

print_success "Prerequisites check completed"

# Step 2: Run QA Tests
print_header "2. Quality Assurance Validation"

print_status "Running comprehensive QA tests..."
if ! ./run_qa_tests.sh; then
    print_error "QA tests failed. Deployment aborted."
    exit 1
fi

print_success "QA tests passed - system ready for deployment"

# Step 3: Backup Current System
print_header "3. System Backup"

print_status "Creating system backup..."

# Backup database
print_status "Backing up database..."
python manage.py dumpdata --natural-foreign --natural-primary > "$BACKUP_DIR/database_backup.json"

# Backup media files
print_status "Backing up media files..."
if [ -d "media" ]; then
    cp -r media "$BACKUP_DIR/"
fi

# Backup configuration
print_status "Backing up configuration..."
cp .env "$BACKUP_DIR/.env.backup" 2>/dev/null || echo "No .env file found"
cp -r logs "$BACKUP_DIR/" 2>/dev/null || echo "No logs directory found"

print_success "System backup completed: $BACKUP_DIR"

# Step 4: Dependencies and Environment
print_header "4. Environment Setup"

print_status "Installing/updating dependencies..."
pip install -r requirements.txt --upgrade

print_status "Installing production dependencies..."
pip install gunicorn psycopg2-binary redis celery[redis]

# Install monitoring tools
pip install sentry-sdk django-prometheus

print_success "Dependencies installed"

# Step 5: Google Cloud Setup
print_header "5. Google Cloud Configuration"

print_status "Setting up Google Cloud resources..."

# Check if Google Cloud is configured
if [ ! -f "service-account-key.json" ]; then
    print_warning "Google Cloud service account not found. Running setup..."
    if [ -f "setup_google_cloud.sh" ]; then
        ./setup_google_cloud.sh
    else
        print_error "Google Cloud setup script not found"
        exit 1
    fi
fi

# Verify Google Cloud configuration
print_status "Verifying Google Cloud configuration..."
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    print_success "Google Cloud credentials configured"
else
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
    print_info "Set GOOGLE_APPLICATION_CREDENTIALS to: $GOOGLE_APPLICATION_CREDENTIALS"
fi

# Step 6: Database Migration
print_header "6. Database Migration"

print_status "Running database migrations..."
python manage.py migrate --noinput

print_status "Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@faktulove.com', 'secure_password_123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

print_success "Database migration completed"

# Step 7: Static Files and Media
print_header "7. Static Files Configuration"

print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear

print_status "Setting up media directories..."
mkdir -p media/documents media/uploads media/exports
chmod 755 media media/documents media/uploads media/exports

print_success "Static files configured"

# Step 8: Security Configuration
print_header "8. Security Hardening"

print_status "Applying security configurations..."

# Update settings for production
cat << 'EOF' > production_settings.py
from faktury_projekt.settings import *
import os

# Production security settings
DEBUG = False
ALLOWED_HOSTS = ['faktulove.pl', 'www.faktulove.pl', 'app.faktulove.pl', '*.faktulove.pl']

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = True

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['OPTIONS'] = {
    'MAX_CONNS': 20,
    'MIN_CONNS': 2,
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}

# OCR Production Settings
OCR_PROCESSING_TIMEOUT = 30
OCR_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
OCR_CONCURRENT_LIMIT = 50
OCR_RETRY_ATTEMPTS = 3

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'FaktuLove OCR <noreply@faktulove.pl>'

# Sentry for error monitoring
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
EOF

print_success "Security configuration applied"

print_header "🎉 PRODUCTION DEPLOYMENT COMPLETED!"

print_info "Next Steps:"
echo "1. Configure web server (Nginx/Apache)"
echo "2. Set up SSL certificates"
echo "3. Configure systemd services"
echo "4. Set up monitoring and alerts"
echo "5. Configure backup procedures"
echo ""

print_success "🚀 FaktuLove OCR is ready for production!"
print_success "Deploy with confidence - all tests passed!"

echo ""
echo "========================================"
echo "🎉 DEPLOYMENT SCRIPT COMPLETE! 🎉"
echo "========================================"
