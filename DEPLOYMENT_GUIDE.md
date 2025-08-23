# FaktuLove AI OCR - Deployment Guide

## 🚀 **System jest gotowy do wdrożenia!**

Kompletna implementacja AI-Powered Invoice OCR została zakończona. Ten przewodnik przeprowadzi Cię przez proces wdrożenia krok po kroku.

## 📋 Pre-Deployment Checklist

### ✅ **Wymagania systemowe**
- Python 3.8+
- Django 4.2+
- Redis Server
- PostgreSQL (zalecane dla produkcji)
- Google Cloud Account z Document AI API

### ✅ **Sprawdź zaimplementowane komponenty**
```bash
# Weryfikacja plików
ls faktury/services/document_ai_service.py     # ✓ AI Service
ls faktury/services/file_upload_service.py    # ✓ File Upload
ls faktury/tasks.py                           # ✓ Celery Tasks
ls faktury/templates/faktury/ocr/             # ✓ Templates
ls faktury/management/commands/ocr_*.py       # ✓ Management Commands
```

## 🔧 **Phase 1: Environment Setup**

### 1. **Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import google.cloud.documentai; print('Google Cloud Document AI: OK')"
python -c "import celery; print('Celery: OK')"
python -c "import redis; print('Redis: OK')"
```

### 2. **Environment Variables**
Create `.env` file from template:
```bash
cp .env.example .env
```

Configure required variables:
```bash
# Django Settings
SECRET_KEY=your-unique-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/faktulove

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
DOCUMENT_AI_PROCESSOR_ID=your-processor-id

# Redis for Celery
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=your-smtp-server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. **Create Media Directories**
```bash
mkdir -p media/ocr_uploads
chmod 755 media
chmod 755 media/ocr_uploads
```

## ☁️ **Phase 2: Google Cloud Setup**

### 1. **Create Google Cloud Project**
```bash
# Install Google Cloud SDK first
# https://cloud.google.com/sdk/docs/install

# Login and create project
gcloud auth login
gcloud projects create faktulove-ocr-prod --name="FaktuLove OCR Production"
gcloud config set project faktulove-ocr-prod
```

### 2. **Enable Required APIs**
```bash
# Enable Document AI API
gcloud services enable documentai.googleapis.com

# Enable Cloud Storage (for file storage)
gcloud services enable storage.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled
```

### 3. **Create Document AI Processor**
```bash
# Create Invoice Processor
gcloud ai document-processors create \
  --location=eu \
  --display-name="FaktuLove Invoice Parser" \
  --type=INVOICE_PROCESSOR

# Note the processor ID from output
```

### 4. **Setup Service Account**
```bash
# Create service account
gcloud iam service-accounts create faktulove-ocr \
  --description="FaktuLove OCR Service Account" \
  --display-name="FaktuLove OCR"

# Grant necessary permissions
gcloud projects add-iam-policy-binding faktulove-ocr-prod \
  --member="serviceAccount:faktulove-ocr@faktulove-ocr-prod.iam.gserviceaccount.com" \
  --role="roles/documentai.apiUser"

# Create and download key
gcloud iam service-accounts keys create ./service-account-key.json \
  --iam-account=faktulove-ocr@faktulove-ocr-prod.iam.gserviceaccount.com

# Secure the key file
chmod 600 service-account-key.json
```

## 🗄️ **Phase 3: Database Setup**

### 1. **Run Migrations**
```bash
# Create and apply migrations
python manage.py makemigrations faktury
python manage.py migrate

# Verify OCR tables were created
python manage.py dbshell -c "\dt faktury_document*"
```

### 2. **Create Superuser**
```bash
python manage.py createsuperuser
```

### 3. **Load Initial Data (Optional)**
```bash
# If you have fixtures
python manage.py loaddata initial_data.json
```

## 📦 **Phase 4: Redis & Celery Setup**

### 1. **Install and Configure Redis**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### 2. **Test Celery Connection**
```bash
# Test Celery can connect to Redis
python manage.py shell -c "
from faktury.tasks import process_ocr_document
print('Celery connection: OK')
"
```

### 3. **Create Systemd Services (Linux Production)**

**Celery Worker Service:**
```bash
sudo tee /etc/systemd/system/faktulove-celery.service > /dev/null <<EOF
[Unit]
Description=FaktuLove Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
EnvironmentFile=/path/to/your/.env
WorkingDirectory=/path/to/faktulove
ExecStart=/path/to/venv/bin/celery multi start worker1 \
    -A faktury_projekt -l info \
    --pidfile=/var/run/celery/%%n.pid \
    --logfile=/var/log/celery/%%n%%I.log
ExecStop=/path/to/venv/bin/celery multi stopwait worker1 \
    --pidfile=/var/run/celery/%%n.pid
ExecReload=/path/to/venv/bin/celery multi restart worker1 \
    -A faktury_projekt -l info \
    --pidfile=/var/run/celery/%%n.pid \
    --logfile=/var/log/celery/%%n%%I.log

[Install]
WantedBy=multi-user.target
EOF

# Create directories
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown www-data:www-data /var/run/celery /var/log/celery

# Enable and start
sudo systemctl enable faktulove-celery
sudo systemctl start faktulove-celery
```

**Celery Beat Service:**
```bash
sudo tee /etc/systemd/system/faktulove-celery-beat.service > /dev/null <<EOF
[Unit]
Description=FaktuLove Celery Beat
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
EnvironmentFile=/path/to/your/.env
WorkingDirectory=/path/to/faktulove
ExecStart=/path/to/venv/bin/celery -A faktury_projekt beat -l info \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable faktulove-celery-beat
sudo systemctl start faktulove-celery-beat
```

## 🌐 **Phase 5: Web Server Setup**

### 1. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

### 2. **Configure Nginx (Recommended)**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # OCR file uploads - increase limits
    client_max_body_size 10M;
    
    location /static/ {
        alias /path/to/faktulove/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/faktulove/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # OCR upload timeouts
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

### 3. **Configure Gunicorn**
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
tee gunicorn.conf.py > /dev/null <<EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300  # OCR processing timeout
keepalive = 5
EOF

# Run Gunicorn
gunicorn faktury_projekt.wsgi:application -c gunicorn.conf.py
```

## 🧪 **Phase 6: Testing & Verification**

### 1. **Test Basic Functionality**
```bash
# Test Django
python manage.py check
python manage.py test faktury.tests

# Test OCR System
python manage.py shell -c "
from faktury.services.document_ai_service import get_document_ai_service
service = get_document_ai_service()
print('OCR Service initialized successfully')
"
```

### 2. **Test File Upload**
```bash
# Create test upload directory
mkdir -p media/test_uploads

# Test file permissions
touch media/test_uploads/test.pdf
rm media/test_uploads/test.pdf
```

### 3. **Test Celery Tasks**
```bash
# Test Celery worker
celery -A faktury_projekt inspect active

# Test Redis connection
python manage.py shell -c "
import redis
r = redis.Redis.from_url('redis://localhost:6379/0')
r.ping()
print('Redis connection: OK')
"
```

### 4. **Test OCR Statistics**
```bash
# Run OCR statistics command
python manage.py ocr_stats --days 30 --format table
```

## 📊 **Phase 7: Monitoring Setup**

### 1. **Setup Logging**
Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/faktulove/ocr.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'faktury.services': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'faktury.tasks': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. **Create Monitoring Cron Jobs**
```bash
# Add to crontab
crontab -e

# OCR cleanup (daily at 2 AM)
0 2 * * * /path/to/venv/bin/python /path/to/faktulove/manage.py ocr_cleanup --force

# OCR statistics (daily at 6 AM)
0 6 * * * /path/to/venv/bin/python /path/to/faktulove/manage.py ocr_stats --days 1 --format json > /var/log/faktulove/daily_stats.json
```

### 3. **Health Check Endpoint**
Test system health:
```bash
curl -f http://localhost:8000/admin/ || echo "Django not responding"
curl -f http://localhost:8000/ocr/api/statistics/ || echo "OCR API not working"
```

## 🔒 **Phase 8: Security & Compliance**

### 1. **SSL Certificate (Production)**
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 2. **Firewall Configuration**
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 6379   # Redis (internal only)
```

### 3. **File Permissions**
```bash
# Secure application files
find /path/to/faktulove -type f -exec chmod 644 {} \;
find /path/to/faktulove -type d -exec chmod 755 {} \;
chmod 600 /path/to/faktulove/.env
chmod 600 /path/to/faktulove/service-account-key.json

# Media directory permissions
chown -R www-data:www-data media/
chmod -R 755 media/
```

## 🚀 **Phase 9: Go Live!**

### 1. **Final Pre-Launch Checklist**
- [ ] Environment variables configured
- [ ] Google Cloud Document AI working
- [ ] Database migrations applied
- [ ] Redis server running
- [ ] Celery workers running
- [ ] SSL certificate installed
- [ ] File permissions set correctly
- [ ] Monitoring and logging configured
- [ ] Backup strategy in place

### 2. **Launch Commands**
```bash
# Start all services
sudo systemctl start redis-server
sudo systemctl start faktulove-celery
sudo systemctl start faktulove-celery-beat
sudo systemctl start nginx

# Verify everything is running
sudo systemctl status redis-server
sudo systemctl status faktulove-celery
sudo systemctl status faktulove-celery-beat
sudo systemctl status nginx

# Check logs
sudo journalctl -u faktulove-celery -f
tail -f /var/log/faktulove/ocr.log
```

### 3. **Post-Launch Verification**
```bash
# Test complete OCR workflow
# 1. Visit /ocr/upload/
# 2. Upload test invoice
# 3. Monitor processing status
# 4. Verify invoice creation

# Check OCR statistics
python manage.py ocr_stats --days 1
```

## 📈 **Monitoring & Maintenance**

### **Daily Monitoring**
- Check Celery worker status
- Review OCR processing logs
- Monitor file storage usage
- Check Google Cloud usage/costs

### **Weekly Maintenance**
- Review OCR accuracy statistics
- Clean up old processed files
- Update dependencies if needed
- Check system resource usage

### **Monthly Reviews**
- Analyze OCR performance trends
- Review and optimize processing settings
- Update confidence thresholds if needed
- Plan for scaling if usage grows

## 🎯 **Success Metrics**

Monitor these KPIs:
- **Processing Success Rate**: >95%
- **Average Processing Time**: <15 seconds
- **Confidence Score**: >85% average
- **Auto-Creation Rate**: >60%
- **User Adoption**: Track monthly active users

## 🆘 **Troubleshooting**

### **Common Issues**

**OCR Processing Fails:**
```bash
# Check Google Cloud credentials
python manage.py shell -c "
import os
print(f'GOOGLE_APPLICATION_CREDENTIALS: {os.getenv(\"GOOGLE_APPLICATION_CREDENTIALS\")}')
"

# Test Document AI connection
python manage.py shell -c "
from faktury.services.document_ai_service import DocumentAIService
service = DocumentAIService()
print(service.validate_processor_availability())
"
```

**Celery Workers Not Processing:**
```bash
# Check Redis connection
redis-cli ping

# Check Celery worker status
celery -A faktury_projekt inspect active

# Restart workers
sudo systemctl restart faktulove-celery
```

**File Upload Errors:**
```bash
# Check media directory permissions
ls -la media/
ls -la media/ocr_uploads/

# Check disk space
df -h
```

## 🎉 **Congratulations!**

Twój system AI-Powered Invoice OCR jest teraz uruchomiony i gotowy do przetwarzania faktur! 

**Następne kroki:**
1. Przetestuj system z rzeczywistymi fakturami
2. Dostosuj progi pewności na podstawie wyników
3. Przeszkol użytkowników w korzystaniu z systemu
4. Monitoruj wydajność i dokładność

**Wsparcie:**
- Dokumentacja: `OCR_IMPLEMENTATION_GUIDE.md`
- Komendy zarządzania: `python manage.py help ocr_cleanup`
- Statystyki: `python manage.py ocr_stats`
- Logi: `/var/log/faktulove/ocr.log`

**🚀 System jest gotowy do produkcji!**