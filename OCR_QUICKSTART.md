# 🚀 FaktuLove OCR - Quick Start Guide

## 📋 Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Google Cloud Account (for production)
- Redis (included in Docker setup)

## ⚡ Quick Setup (5 minutes)

### 1. Clone and Setup Environment

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd faktulove

# Make scripts executable
chmod +x setup_development_env.sh
chmod +x setup_google_cloud.sh
chmod +x test_ocr_poc.py

# Run development environment setup
./setup_development_env.sh
```

### 2. Configure Environment Variables

```bash
# Copy .env template (if not exists)
cp .env.example .env

# Edit .env file
nano .env
```

Required variables:
```env
# For development (mock service)
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://faktulove_user:faktulove_password@localhost:5432/faktulove_db
REDIS_URL=redis://localhost:6379/0

# For production (Google Cloud)
GOOGLE_CLOUD_PROJECT=faktulove-ocr
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
DOCUMENT_AI_PROCESSOR_ID=your-processor-id
```

### 3. Start Services

```bash
# Start Docker services (PostgreSQL, Redis)
docker-compose up -d postgres redis

# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (first time only)
python manage.py createsuperuser

# Start development server
./start_dev.sh
```

## 🧪 Test OCR with Mock Service

### 1. Run POC Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python test_ocr_poc.py
```

### 2. Manual Testing via Web Interface

1. Open browser: http://localhost:8000
2. Login with your credentials
3. Navigate to: **Dokumenty → OCR Upload**
4. Upload a test invoice (PDF/JPG/PNG)
5. View processing status
6. Review extracted data

### 3. Test via API

```bash
# Upload document
curl -X POST http://localhost:8000/ocr/api/upload/ \
  -H "Authorization: Token your-api-token" \
  -F "document=@test_invoice.pdf"

# Check status
curl http://localhost:8000/ocr/api/status/{document_id}/ \
  -H "Authorization: Token your-api-token"
```

## 🔧 Google Cloud Setup (Production)

### 1. Run Setup Script

```bash
# Configure Google Cloud
./setup_google_cloud.sh

# Follow the prompts to:
# - Create project
# - Enable APIs
# - Create service account
# - Setup Document AI processor
```

### 2. Test with Real Document AI

```bash
# Update .env with Google Cloud credentials
nano .env

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Switch to production service in settings
# Edit faktury/services/__init__.py
# Change: document_ai_service = MockDocumentAIService()
# To: document_ai_service = DocumentAIService()

# Restart server
./start_dev.sh
```

## 📊 Monitor Processing

### Celery Flower Dashboard
```bash
# Access monitoring dashboard
open http://localhost:5555
```

### Django Admin
```bash
# View OCR results in admin
open http://localhost:8000/admin/faktury/ocrresult/
```

### Command Line
```bash
# Check Celery workers
celery -A faktury_projekt inspect active

# View logs
tail -f celery.log

# Database statistics
python manage.py shell
>>> from faktury.models import OCRResult
>>> OCRResult.objects.count()
>>> OCRResult.objects.filter(confidence_score__gte=95).count()
```

## 🎯 Common Use Cases

### Process Single Invoice
```python
# Via Django shell
python manage.py shell

from faktury.services.file_upload_service import FileUploadService
from faktury.tasks import process_ocr_document
from django.contrib.auth.models import User

# Get user
user = User.objects.get(username='admin')

# Upload file
with open('invoice.pdf', 'rb') as f:
    from django.core.files.uploadedfile import SimpleUploadedFile
    file = SimpleUploadedFile('invoice.pdf', f.read(), content_type='application/pdf')
    
upload_service = FileUploadService()
document = upload_service.handle_upload(file, user)

# Process OCR
process_ocr_document.delay(document.id)
```

### Batch Processing
```python
# Process multiple files
import os
from pathlib import Path

invoice_dir = Path('./invoices')
for invoice_file in invoice_dir.glob('*.pdf'):
    with open(invoice_file, 'rb') as f:
        # ... upload and process
```

## 🐛 Troubleshooting

### Issue: Celery not processing tasks
```bash
# Check if workers are running
ps aux | grep celery

# Restart workers
./stop_dev.sh
./start_dev.sh

# Check Redis connection
redis-cli ping
```

### Issue: Low OCR accuracy
```bash
# Check document quality
# Minimum 150 DPI recommended

# View confidence scores
python manage.py shell
>>> from faktury.models import OCRResult
>>> results = OCRResult.objects.order_by('-created_at')[:10]
>>> for r in results:
...     print(f"{r.document.original_filename}: {r.confidence_score}%")
```

### Issue: Google Cloud authentication error
```bash
# Verify credentials
gcloud auth application-default login

# Check service account key
ls -la service-account-key.json

# Test authentication
python -c "from google.cloud import documentai; print('Auth OK')"
```

## 📚 Additional Resources

- [OCR Implementation Guide](OCR_IMPLEMENTATION_GUIDE.md)
- [GDPR Security Assessment](GDPR_SECURITY_ASSESSMENT.md)
- [API Documentation](https://app.faktulove.pl/api/docs)
- [Google Document AI Docs](https://cloud.google.com/document-ai/docs)

## 🆘 Support

- Technical Issues: dev@faktulove.pl
- Business Questions: support@faktulove.pl
- Emergency: +48 XXX XXX XXX

---

**Last Updated**: $(date +%Y-%m-%d)  
**Version**: 1.0  
**Status**: Development/Testing