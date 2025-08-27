# PaddleOCR Deployment Guide

This guide provides comprehensive instructions for deploying FaktuLove with PaddleOCR as the primary OCR engine.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Performance Tuning](#performance-tuning)
9. [Maintenance](#maintenance)

## Overview

PaddleOCR is now the primary OCR engine for FaktuLove, providing:

- **Superior Polish Language Support**: Optimized for Polish invoice processing
- **Advanced Image Preprocessing**: Enhanced document quality before OCR
- **Intelligent Fallback System**: Automatic fallback to Tesseract/EasyOCR on failures
- **Performance Monitoring**: Real-time monitoring and optimization
- **Memory Management**: Intelligent memory usage and cleanup
- **Confidence Scoring**: Advanced confidence calculation with spatial analysis

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│  Django Web App  │───▶│  PaddleOCR      │
└─────────────────┘    └──────────────────┘    │  Service        │
                                │               └─────────────────┘
                                ▼                        │
                       ┌──────────────────┐             ▼
                       │  Celery Worker   │    ┌─────────────────┐
                       │  (PaddleOCR)     │───▶│  Fallback       │
                       └──────────────────┘    │  Engines        │
                                │               │  (Tesseract,    │
                                ▼               │   EasyOCR)      │
                       ┌──────────────────┐    └─────────────────┘
                       │  Redis Cache     │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  PostgreSQL DB   │
                       └──────────────────┘
```

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04/22.04 LTS or similar Linux distribution
- **Memory**: Minimum 4GB RAM, Recommended 8GB+ RAM
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Storage**: Minimum 10GB free space for models and cache
- **Docker**: Version 20.10+ with docker-compose

### Software Dependencies

- Docker and Docker Compose
- Python 3.11+ (if running without Docker)
- Git for source code management

### Network Requirements

- Internet access for model downloads (first-time setup)
- Ports 8000 (web), 5555 (Flower), 6379 (Redis), 5432 (PostgreSQL)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/faktulove.git
cd faktulove
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 3. Required Environment Variables

```bash
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=false
ALLOWED_HOSTS=your-domain.com,localhost

# Database Configuration
DATABASE_URL=postgresql://faktulove_user:faktulove_password@postgres:5432/faktulove_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# PaddleOCR Configuration
PADDLEOCR_ENABLED=true
PADDLEOCR_PRIMARY=true
USE_PADDLEOCR=true
PADDLEOCR_USE_GPU=false
PADDLEOCR_LANGUAGES=pl,en
PADDLEOCR_MAX_MEMORY=800
PADDLEOCR_FALLBACK_ENABLED=true

# Performance Tuning
PADDLEOCR_MAX_WORKERS=2
PADDLEOCR_BATCH_SIZE=1
PADDLEOCR_MEMORY_OPTIMIZATION=basic
PADDLEOCR_MODEL_CACHING=true
```

## Configuration

### PaddleOCR Settings

The PaddleOCR configuration is managed through Django settings and environment variables:

#### Core Configuration

```python
PADDLEOCR_CONFIG = {
    'enabled': True,
    'languages': ['pl', 'en'],
    'use_gpu': False,
    'max_memory_mb': 800,
    'timeout': 30,
    'max_retries': 2,
}
```

#### Performance Configuration

```python
PADDLEOCR_PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 3,
    'worker_pool_size': 2,
    'memory_optimization_level': 'basic',
    'enable_model_caching': True,
}
```

#### Fallback Configuration

```python
OCR_ENGINE_PRIORITY = [
    'paddleocr',    # Primary engine
    'tesseract',    # Secondary fallback
    'easyocr',      # Tertiary fallback
]
```

### Polish Optimization

PaddleOCR includes specialized Polish language optimizations:

- **NIP Validation**: Automatic NIP number validation with checksum
- **Date Format Recognition**: Polish date format parsing
- **Currency Parsing**: Polish złoty (PLN) amount recognition
- **Company Type Detection**: Recognition of Polish company types (Sp. z o.o., S.A., etc.)
- **Spatial Analysis**: Layout-aware confidence scoring

## Deployment

### Quick Deployment

Use the automated deployment script:

```bash
# Make deployment script executable
chmod +x deploy_paddleocr.sh

# Run deployment
./deploy_paddleocr.sh deploy
```

### Manual Deployment

#### 1. Build Docker Images

```bash
# Build main application
docker-compose -f docker-compose.paddleocr.yml build

# Pull required images
docker-compose -f docker-compose.paddleocr.yml pull
```

#### 2. Initialize Database

```bash
# Start database
docker-compose -f docker-compose.paddleocr.yml up -d postgres redis

# Run migrations
docker-compose -f docker-compose.paddleocr.yml run --rm web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.paddleocr.yml run --rm web python manage.py createsuperuser
```

#### 3. Download PaddleOCR Models

```bash
# Pre-download models (optional but recommended)
docker-compose -f docker-compose.paddleocr.yml run --rm web python -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
print('Models downloaded successfully')
"
```

#### 4. Start All Services

```bash
# Start all services
docker-compose -f docker-compose.paddleocr.yml up -d

# Check status
docker-compose -f docker-compose.paddleocr.yml ps
```

### Production Deployment

For production environments, additional considerations:

#### 1. SSL/TLS Configuration

```bash
# Add SSL certificates
mkdir -p ssl/
# Copy your SSL certificates to ssl/ directory

# Update docker-compose with SSL configuration
# Add nginx reverse proxy with SSL termination
```

#### 2. Resource Limits

```yaml
# In docker-compose.paddleocr.yml
deploy:
  resources:
    limits:
      memory: 1.5G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

#### 3. Backup Configuration

```bash
# Setup automated backups
crontab -e

# Add backup job (daily at 2 AM)
0 2 * * * /path/to/faktulove/backup_paddleocr.sh
```

## Monitoring

### Health Checks

#### Automated Monitoring

```bash
# Start monitoring
./monitor_paddleocr.sh monitor

# Continuous monitoring
./monitor_paddleocr.sh watch

# Check specific components
./monitor_paddleocr.sh paddleocr
./monitor_paddleocr.sh services
```

#### Django Management Commands

```bash
# Basic hbash
# Check fallback configuration
docker-compose -f docker-compose.paddleocr.yml exec web python manage.py shell -c "
from faktury.services.ocr_service_factory import OCRServiceFactory
print(OCRServiceFactory.get_available_implementations())
"

# Test individual engines
docker-compose -f docker-compose.paddleocr.yml exec web python manage.py test faktury.tests.test_ocr_integration
```

### Debugging Commands

#### Check Service Status

```bash
# PaddleOCR service status
docker-compose -f docker-compose.paddleocr.yml exec web python manage.py validate_ocr_config

# Test OCR processing
docker-compose -f docker-compose.paddleocr.yml exec web python manage.py shell -c "
from faktury.services.paddle_ocr_service import PaddleOCRService
service = PaddleOCRService()
print('Available:', service.validate_processor_availability())
"
```

#### Performance Analysis

```bash
# Memory usage
docker stats --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}"

# Disk usage
du -sh paddle_models/ .ocr_cache/ .ocr_result_cache/

# Process analysis
docker-compose -f docker-compose.paddleocr.yml exec paddleocr_worker ps aux
```

## Performance Tuning

### Memory Optimization

#### 1. Adjust Memory Limits

```bash
# Conservative settings (low memory systems)
export PADDLEOCR_MAX_MEMORY=400
export PADDLEOCR_MEMORY_OPTIMIZATION=aggressive
export PADDLEOCR_MAX_WORKERS=1

# High-performance settings (high memory systems)
export PADDLEOCR_MAX_MEMORY=1200
export PADDLEOCR_MEMORY_OPTIMIZATION=basic
export PADDLEOCR_MAX_WORKERS=3
```

#### 2. Model Caching

```bash
# Enable aggressive model caching
export PADDLEOCR_MODEL_CACHING=true
export PADDLEOCR_MODEL_CACHE_SIZE=3
export PADDLEOCR_MODEL_CACHE_TTL=7200
```

### CPU Optimization

#### 1. Thread Configuration

```bash
# Optimize for CPU cores
export OMP_NUM_THREADS=4
export PADDLEOCR_CPU_THREADS=4
export PADDLEOCR_CPU_OPTIMIZATION=high
```

#### 2. Batch Processing

```bash
# Enable batch processing for high volume
export PADDLEOCR_ENABLE_BATCH_PROCESSING=true
export PADDLEOCR_MAX_BATCH_SIZE=3
export PADDLEOCR_BATCH_TIMEOUT=10
```

### Network Optimization

#### 1. Connection Pooling

```bash
# Optimize database connections
export DATABASE_CONN_MAX_AGE=600
export DATABASE_CONN_HEALTH_CHECKS=true

# Redis connection pooling
export REDIS_CONNECTION_POOL_SIZE=50
```

## Maintenance

### Regular Maintenance Tasks

#### 1. Model Updates

```bash
# Check for model updates (monthly)
docker-compose -f docker-compose.paddleocr.yml run --rm web python -c "
from paddleocr import PaddleOCR
# This will download latest models if available
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
"
```

#### 2. Cache Cleanup

```bash
# Clean old cache files (weekly)
./monitor_paddleocr.sh cleanup

# Manual cleanup
find .ocr_cache/ -type f -mtime +7 -delete
find .ocr_result_cache/ -type f -mtime +7 -delete
```

#### 3. Log Rotation

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/faktulove

# Add configuration:
/path/to/faktulove/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

#### 4. Database Maintenance

```bash
# Vacuum database (monthly)
docker-compose -f docker-compose.paddleocr.yml exec postgres psql -U faktulove_user -d faktulove_db -c "VACUUM ANALYZE;"

# Update statistics
docker-compose -f docker-compose.paddleocr.yml exec web python manage.py update_statistics
```

### Backup and Recovery

#### 1. Automated Backups

```bash
# Create backup script
cat > backup_paddleocr.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose -f docker-compose.paddleocr.yml exec postgres pg_dump -U faktulove_user faktulove_db > "$BACKUP_DIR/database.sql"

# Backup media files
cp -r media/ "$BACKUP_DIR/"

# Backup models
cp -r paddle_models/ "$BACKUP_DIR/"

# Backup configuration
cp .env "$BACKUP_DIR/"

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup_paddleocr.sh
```

#### 2. Recovery Procedures

```bash
# Restore from backup
BACKUP_DIR="backups/20241201_120000"

# Restore database
docker-compose -f docker-compose.paddleocr.yml exec -T postgres psql -U faktulove_user -d faktulove_db < "$BACKUP_DIR/database.sql"

# Restore media files
cp -r "$BACKUP_DIR/media/" ./

# Restore models
cp -r "$BACKUP_DIR/paddle_models/" ./
```

### Security Updates

#### 1. Regular Updates

```bash
# Update base images (monthly)
docker-compose -f docker-compose.paddleocr.yml pull

# Rebuild with latest dependencies
docker-compose -f docker-compose.paddleocr.yml build --no-cache

# Update Python packages
pip install --upgrade -r requirements.txt -r requirements_ocr.txt
```

#### 2. Security Scanning

```bash
# Scan Docker images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image faktulove_web

# Check Python dependencies
pip-audit
```

## Support and Resources

### Documentation

- [PaddleOCR Official Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)

### Community

- [PaddleOCR GitHub Issues](https://github.com/PaddlePaddle/PaddleOCR/issues)
- [FaktuLove Support](mailto:support@faktulove.pl)

### Professional Support

For enterprise support and custom implementations, contact:
- Email: enterprise@faktulove.pl
- Phone: +48 XXX XXX XXX

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Compatibility**: FaktuLove v2.0+ with PaddleOCR v2.7+