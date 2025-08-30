#!/bin/bash
# Full Production Deployment Script for FaktuLove
# Deploys complete local version to production server

set -e

SERVER="admin@ec2-13-60-160-136.eu-north-1.compute.amazonaws.com"
KEY_PATH="/home/ooxo/.ssh/klucz1.pem"
DOMAIN="faktulove.ooxo.pl"
REMOTE_PATH="/home/admin/faktulove"

echo "🚀 FULL PRODUCTION DEPLOYMENT - FaktuLove"
echo "=========================================="
echo "🌐 Domain: $DOMAIN"
echo "🖥️ Server: $SERVER"
echo "📁 Remote Path: $REMOTE_PATH"
echo ""

# Stop existing services
echo "⏹️ Stopping existing services..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
# Stop Django/Gunicorn
pkill -f gunicorn || true
pkill -f "manage.py runserver" || true

# Stop Celery workers
pkill -f celery || true

# Stop OCR service
pkill -f production_ocr_service.py || true

echo "✅ Services stopped"
EOF

# Create backup of current version
echo "💾 Creating backup of current version..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
cd /home/admin/
if [ -d "faktulove" ]; then
    BACKUP_NAME="faktulove_backup_$(date +%Y%m%d_%H%M%S)"
    echo "📦 Creating backup: $BACKUP_NAME"
    cp -r faktulove "$BACKUP_NAME"
    echo "✅ Backup created: $BACKUP_NAME"
fi
EOF

# Sync entire local directory to server (excluding some files)
echo "📤 Syncing local files to server..."
rsync -avz --delete \
    --exclude='.git/' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='db.sqlite3' \
    --exclude='logs/' \
    --exclude='media/' \
    --exclude='staticfiles/' \
    --exclude='node_modules/' \
    --exclude='.cursor/' \
    --exclude='.vscode/' \
    --exclude='*.log' \
    -e "ssh -i $KEY_PATH" \
    ./ "$SERVER:$REMOTE_PATH/"

echo "✅ Files synced to server"

# Setup production environment on server
echo "🔧 Setting up production environment..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
cd /home/admin/faktulove

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing/updating Python packages..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, installing basic packages..."
    pip install django gunicorn celery redis pillow
fi

# Install OCR packages
echo "🔍 Installing OCR packages..."
pip install pytesseract opencv-python easyocr || echo "⚠️ Some OCR packages failed"

echo "✅ Python packages installed"
EOF

# Setup database and static files
echo "🗄️ Setting up database and static files..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
cd /home/admin/faktulove
source venv/bin/activate

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell << 'PYTHON'
from django.contrib.auth.models import User
from faktury.models import Firma

username = 'ooxo'
password = 'ooxo'
email = 'admin@faktulove.ooxo.pl'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.save()
    print(f"✅ Admin user '{username}' updated")
except User.DoesNotExist:
    user = User.objects.create_superuser(username, email, password)
    print(f"✅ Admin user '{username}' created")

# Create company if doesn't exist
try:
    firma = Firma.objects.get(user=user)
    print(f"✅ Company exists: {firma.nazwa}")
except Firma.DoesNotExist:
    firma = Firma.objects.create(
        user=user,
        nazwa="FaktuLove Production",
        adres="ul. Produkcyjna 1",
        kod_pocztowy="00-001", 
        miasto="Warszawa",
        nip="1234567890",
        regon="123456789",
        email=email,
        telefon="+48 123 456 789"
    )
    print(f"✅ Company created: {firma.nazwa}")
PYTHON

echo "✅ Database setup completed"
EOF

# Create production configuration files
echo "⚙️ Creating production configuration..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
cd /home/admin/faktulove

# Create production settings if doesn't exist
if [ ! -f "production_settings.py" ]; then
cat > production_settings.py << 'SETTINGS'
from faktulove.settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['faktulove.ooxo.pl', 'ec2-13-60-160-136.eu-north-1.compute.amazonaws.com', 'localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# OCR Settings
OCR_SERVICE_URL = 'http://localhost:8001'
SETTINGS
fi

# Create gunicorn config
cat > gunicorn.conf.py << 'GUNICORN'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "admin"
group = "admin"
tmp_upload_dir = None
logfile = "/home/admin/faktulove/logs/gunicorn.log"
loglevel = "info"
access_logfile = "/home/admin/faktulove/logs/gunicorn_access.log"
error_logfile = "/home/admin/faktulove/logs/gunicorn_error.log"
GUNICORN

# Create logs directory
mkdir -p logs

echo "✅ Production configuration created"
EOF

# Start production services
echo "🚀 Starting production services..."
ssh -i "$KEY_PATH" "$SERVER" << 'EOF'
cd /home/admin/faktulove
source venv/bin/activate

# Start Gunicorn
echo "🌐 Starting Gunicorn (Django)..."
nohup gunicorn --config gunicorn.conf.py faktulove.wsgi:application > logs/gunicorn_startup.log 2>&1 &
GUNICORN_PID=$!

# Wait a moment for Gunicorn to start
sleep 3

# Start Celery workers
echo "⚙️ Starting Celery workers..."
nohup celery -A faktulove worker -l info -Q ocr,cleanup --concurrency=2 > logs/celery.log 2>&1 &
CELERY_PID=$!

# Start OCR service
echo "🔍 Starting OCR service..."
cd /home/admin/
nohup python3 production_ocr_service.py > ocr_service.log 2>&1 &
OCR_PID=$!

# Save PIDs for later management
echo $GUNICORN_PID > /home/admin/faktulove/gunicorn.pid
echo $CELERY_PID > /home/admin/faktulove/celery.pid  
echo $OCR_PID > /home/admin/ocr_service.pid

echo "✅ All services started"
echo "🌐 Gunicorn PID: $GUNICORN_PID"
echo "⚙️ Celery PID: $CELERY_PID"
echo "🔍 OCR Service PID: $OCR_PID"
EOF

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Test deployment
echo "🧪 Testing deployment..."
echo "Testing Django..."
if curl -s -I http://$DOMAIN:8000/ | grep -q "HTTP/1.1"; then
    echo "✅ Django is responding"
else
    echo "❌ Django is not responding"
fi

echo "Testing OCR service..."
if curl -s http://$DOMAIN:8001/health | grep -q "healthy"; then
    echo "✅ OCR service is healthy"
else
    echo "❌ OCR service is not responding"
fi

# Display final status
echo ""
echo "🎉 DEPLOYMENT COMPLETED!"
echo "======================="
echo "🌐 Django: http://$DOMAIN:8000/"
echo "🔐 Admin: http://$DOMAIN:8000/admin/"
echo "🔍 OCR API: http://$DOMAIN:8001/health"
echo "👤 Login: ooxo / ooxo"
echo ""
echo "📊 Service Status:"
ssh -i "$KEY_PATH" "$SERVER" "ps aux | grep -E '(gunicorn|celery|production_ocr)' | grep -v grep | wc -l" | while read count; do
    echo "   Running processes: $count"
done

echo ""
echo "📋 Next steps:"
echo "1. Test admin login: http://$DOMAIN:8000/admin/"
echo "2. Test OCR upload functionality"
echo "3. Monitor logs: ssh -i $KEY_PATH $SERVER 'tail -f /home/admin/faktulove/logs/*.log'"
echo ""
echo "✅ FaktuLove is now running in production!"