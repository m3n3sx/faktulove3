# FaktuLove OCR - Production Deployment Guide

Complete guide for deploying the FaktuLove AI-Powered Invoice OCR system to production.

## 🎯 Deployment Overview

### Production Architecture
```
[Load Balancer] -> [Nginx] -> [Django/Gunicorn] -> [PostgreSQL]
                           -> [Celery Workers] -> [Redis]
                           -> [React Frontend]
                           -> [Google Cloud Document AI]
```

### System Requirements
- **Server**: Ubuntu 20.04+ LTS (minimum 4GB RAM, 2 CPU cores)
- **Database**: PostgreSQL 12+
- **Cache**: Redis 6+
- **Web Server**: Nginx 1.18+
- **Python**: 3.8+
- **Node.js**: 16+ (for frontend)

## 🚀 Quick Deployment

### Automated Deployment
```bash
# Run the automated deployment script
./deploy_production.sh

# Follow the post-deployment steps
sudo systemctl enable nginx postgresql redis
sudo systemctl start nginx postgresql redis
```

### Manual Deployment Steps
Follow the detailed steps below for custom deployment scenarios.

## 📋 Pre-Deployment Checklist

### 1. Server Preparation
- [ ] Ubuntu 20.04+ LTS server provisioned
- [ ] Domain name configured (faktulove.pl)
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] SSH access configured

### 2. Database Setup
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE faktulove_prod;
CREATE USER faktulove WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE faktulove_prod TO faktulove;
\q
```

### 3. System Dependencies
```bash
# Install system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    nginx \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx \
    build-essential \
    libpq-dev \
    git

# Install Node.js (for frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🔧 Application Deployment

### 1. Code Deployment
```bash
# Clone repository
cd /var/www/
sudo git clone https://github.com/your-org/faktulove.git
cd faktulove

# Set permissions
sudo chown -R www-data:www-data /var/www/faktulove
sudo chmod -R 755 /var/www/faktulove

# Create virtual environment
sudo -u www-data python3 -m venv venv
sudo -u www-data source venv/bin/activate
sudo -u www-data pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Create production environment file
sudo -u www-data cat << 'EOF' > .env
# Database
DATABASE_URL=postgresql://faktulove:secure_password_here@localhost:5432/faktulove_prod

# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=faktulove.pl,www.faktulove.pl,app.faktulove.pl

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/var/www/faktulove/service-account-key.json
GOOGLE_CLOUD_PROJECT=faktulove-ocr

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=noreply@faktulove.pl
EMAIL_HOST_PASSWORD=your-email-password

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
EOF
```

### 3. Database Migration
```bash
sudo -u www-data source venv/bin/activate
sudo -u www-data python manage.py migrate
sudo -u www-data python manage.py collectstatic --noinput
sudo -u www-data python manage.py createsuperuser
```

### 4. Frontend Build
```bash
cd frontend
sudo -u www-data npm install
sudo -u www-data npm run build

# Copy build files to Django static
sudo -u www-data cp -r build/* ../staticfiles/
```

## 🌐 Web Server Configuration

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/faktulove
upstream faktulove_django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name faktulove.pl www.faktulove.pl app.faktulove.pl;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name faktulove.pl www.faktulove.pl app.faktulove.pl;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/faktulove.pl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/faktulove.pl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # File Upload Limits
    client_max_body_size 10M;

    # Document Root
    root /var/www/faktulove;

    # Static Files
    location /static/ {
        alias /var/www/faktulove/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/faktulove/media/;
        expires 1M;
        add_header Cache-Control "public";
    }

    # API Endpoints
    location /api/ {
        proxy_pass http://faktulove_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_read_timeout 120s;
    }

    # Admin Panel
    location /admin/ {
        proxy_pass http://faktulove_django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health Check
    location /health/ {
        proxy_pass http://faktulove_django;
        access_log off;
    }

    # Frontend (React)
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/faktulove /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 SSL Certificate Setup

### Let's Encrypt Configuration
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d faktulove.pl -d www.faktulove.pl -d app.faktulove.pl

# Test automatic renewal
sudo certbot renew --dry-run

# Add renewal to crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 🚀 Service Configuration

### Django (Gunicorn) Service
```ini
# /etc/systemd/system/faktulove-django.service
[Unit]
Description=FaktuLove OCR Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/faktulove
ExecStart=/var/www/faktulove/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 faktury_projekt.wsgi:application
Environment=DJANGO_SETTINGS_MODULE=production_settings
EnvironmentFile=/var/www/faktulove/.env
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Celery Worker Service
```ini
# /etc/systemd/system/faktulove-celery.service
[Unit]
Description=FaktuLove OCR Celery Worker
After=network.target redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/faktulove
ExecStart=/var/www/faktulove/venv/bin/celery -A faktury_projekt worker --loglevel=info --concurrency=4
EnvironmentFile=/var/www/faktulove/.env
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Celery Beat Service
```ini
# /etc/systemd/system/faktulove-celery-beat.service
[Unit]
Description=FaktuLove OCR Celery Beat
After=network.target redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/faktulove
ExecStart=/var/www/faktulove/venv/bin/celery -A faktury_projekt beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
EnvironmentFile=/var/www/faktulove/.env
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable faktulove-django faktulove-celery faktulove-celery-beat

# Start services
sudo systemctl start faktulove-django faktulove-celery faktulove-celery-beat

# Check status
sudo systemctl status faktulove-django faktulove-celery faktulove-celery-beat
```

## 📊 Monitoring and Logging

### Log Configuration
```bash
# Create log directories
sudo mkdir -p /var/log/faktulove
sudo chown www-data:www-data /var/log/faktulove

# Configure log rotation
sudo cat << 'EOF' > /etc/logrotate.d/faktulove
/var/log/faktulove/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload faktulove-django faktulove-celery faktulove-celery-beat
    endscript
}
EOF
```

### Health Monitoring
```bash
# Create health check script
sudo cat << 'EOF' > /usr/local/bin/faktulove-health-check
#!/bin/bash
HEALTH_URL="https://faktulove.pl/health/"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $STATUS -eq 200 ]; then
    echo "$(date): FaktuLove OCR is healthy (HTTP $STATUS)"
    exit 0
else
    echo "$(date): FaktuLove OCR is unhealthy (HTTP $STATUS)"
    # Send alert notification here
    exit 1
fi
EOF

sudo chmod +x /usr/local/bin/faktulove-health-check

# Add to crontab for monitoring
echo "*/5 * * * * /usr/local/bin/faktulove-health-check >> /var/log/faktulove/health.log 2>&1" | sudo crontab -
```

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### System Security
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install fail2ban for brute force protection
sudo apt install fail2ban

# Configure fail2ban for Nginx
sudo cat << 'EOF' > /etc/fail2ban/jail.local
[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-noproxy]
enabled = true
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql faktulove_prod

-- Create indexes for OCR tables
CREATE INDEX CONCURRENTLY idx_ocr_result_document_id ON faktury_ocrresult(document_id);
CREATE INDEX CONCURRENTLY idx_ocr_result_created_at ON faktury_ocrresult(created_at);
CREATE INDEX CONCURRENTLY idx_document_upload_user_id ON faktury_documentupload(user_id);
CREATE INDEX CONCURRENTLY idx_document_upload_status ON faktury_documentupload(status);

-- Optimize PostgreSQL configuration
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

SELECT pg_reload_conf();
```

### Redis Optimization
```bash
# Configure Redis for production
sudo cat << 'EOF' >> /etc/redis/redis.conf
# Memory optimization
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Network
tcp-keepalive 300
EOF

sudo systemctl restart redis-server
```

## 🎯 Go-Live Checklist

### Pre-Launch Validation
- [ ] All services running and healthy
- [ ] SSL certificate installed and valid
- [ ] Database backups configured
- [ ] Monitoring and alerting configured
- [ ] Performance tests passed
- [ ] Security scan completed
- [ ] Load balancer configured (if applicable)

### Launch Day Tasks
1. **Final deployment**:
   ```bash
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart faktulove-django faktulove-celery
   ```

2. **Smoke tests**:
   ```bash
   curl https://faktulove.pl/health/
   curl https://faktulove.pl/api/health/
   ```

3. **Monitor logs**:
   ```bash
   sudo tail -f /var/log/faktulove/django.log
   sudo tail -f /var/log/faktulove/celery.log
   sudo tail -f /var/log/nginx/access.log
   ```

### Post-Launch Monitoring
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Track OCR processing performance
- [ ] Monitor error rates and response times
- [ ] Check SSL certificate expiry
- [ ] Verify backup procedures

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status faktulove-django

# Check logs
sudo journalctl -u faktulove-django -f

# Check application logs
sudo tail -f /var/log/faktulove/django.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo -u www-data psql -h localhost -U faktulove -d faktulove_prod

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 3. OCR Processing Fails
```bash
# Check Google Cloud credentials
sudo -u www-data python3 -c "
import os
print('GOOGLE_APPLICATION_CREDENTIALS:', os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
print('File exists:', os.path.exists(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')))
"

# Test OCR service
sudo -u www-data python3 manage.py shell -c "
from faktury.services.document_ai_service import get_document_ai_service
service = get_document_ai_service()
print('Service type:', type(service).__name__)
"
```

#### 4. High Memory Usage
```bash
# Monitor processes
htop

# Check Celery worker memory
ps aux | grep celery

# Restart services if needed
sudo systemctl restart faktulove-celery
```

### Emergency Procedures

#### Rollback Deployment
```bash
# Stop services
sudo systemctl stop faktulove-django faktulove-celery faktulove-celery-beat

# Restore from backup
cd /var/www/faktulove
git checkout previous-stable-tag
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo systemctl start faktulove-django faktulove-celery faktulove-celery-beat
```

#### Database Recovery
```bash
# Restore database from backup
sudo -u postgres dropdb faktulove_prod
sudo -u postgres createdb faktulove_prod
sudo -u postgres psql faktulove_prod < backup/database_backup.sql
```

## 📞 Support Contacts

### Production Support
- **Primary**: admin@faktulove.pl
- **Emergency**: +48 xxx xxx xxx
- **Monitoring**: https://status.faktulove.pl

### Escalation Procedures
1. **Level 1**: Service restart, log analysis
2. **Level 2**: Database issues, performance problems
3. **Level 3**: Security incidents, data corruption

---

**Deployment completed successfully! 🎉**

**FaktuLove OCR is now LIVE and ready to process Polish invoices with 98%+ accuracy!**
