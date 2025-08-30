# Technology Stack & Build System

## Core Framework
- **Django 4.2.23**: Main web framework with Polish localization
- **Python 3.11+**: Required minimum version
- **PostgreSQL/SQLite**: Database backends (SQLite for dev, PostgreSQL for production)

## Frontend
- **React 18.2**: Frontend SPA in `frontend/` directory
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **React Query**: Data fetching and caching

## OCR & AI Stack
- **Tesseract OCR**: Primary OCR engine with Polish language support
- **EasyOCR**: Secondary OCR engine for improved accuracy
- **OpenCV**: Image preprocessing and enhancement
- **PyTorch**: Machine learning framework for OCR models
- **Pillow**: Image processing library

## Infrastructure
- **Redis**: Caching and message broker
- **Celery**: Asynchronous task processing
- **Docker**: Containerization with docker-compose
- **Gunicorn**: WSGI HTTP server for production
- **Nginx**: Reverse proxy and static file serving

## API & Authentication
- **Django REST Framework**: API development
- **JWT Authentication**: Token-based auth with refresh tokens
- **django-allauth**: Social authentication (Google, Facebook)
- **drf-spectacular**: OpenAPI schema generation

## Development Tools
- **django-import-export**: Data import/export functionality
- **django-crispy-forms**: Form rendering with Bootstrap 5
- **WeasyPrint**: PDF generation
- **python-magic**: File type detection

## Common Commands

### Development Setup
```bash
# Start development environment
./start_dev.sh

# Manual development start
source venv/bin/activate
python manage.py runserver
```

### Database Operations
```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Load fixtures
python manage.py loaddata fixtures/initial_data.json
```

### Testing
```bash
# Run all tests
./run_tests.sh

# Run specific test module
python manage.py test faktury.tests.test_ocr_integration

# Run QA tests
./run_qa_tests.sh
```

### OCR Management
```bash
# Test OCR setup
python manage.py test_ocr_setup

# OCR statistics
python manage.py ocr_stats

# Cleanup old OCR files
python manage.py ocr_cleanup
```

### Production Deployment
```bash
# Full production deployment
./deploy_production.sh

# Collect static files
python manage.py collectstatic --noinput

# Start production services
./manage_faktulove.sh start
```

### Docker Operations
```bash
# Start services
docker-compose up -d

# OCR-specific services
docker-compose -f docker-compose.ocr.yml up -d

# View logs
docker-compose logs -f
```

### Celery Tasks
```bash
# Start worker
celery -A faktury_projekt worker -l info

# Start beat scheduler
celery -A faktury_projekt beat -l info

# Monitor with Flower
celery -A faktury_projekt flower
```

## Environment Variables
Key environment variables in `.env`:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account
- `OCR_SERVICE_URL`: OCR microservice endpoint
- `EMAIL_HOST_*`: SMTP configuration