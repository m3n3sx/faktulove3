# Project Structure & Organization

## Root Directory Layout
```
faktulove/                 # Main Django project
├── faktury/              # Core application module
├── frontend/             # React SPA frontend
├── docker/               # Docker configurations
├── logs/                 # Application logs
├── media/                # User uploaded files
├── static/               # Static assets
├── venv/                 # Python virtual environment
└── *.sh                  # Management scripts
```

## Core Application (`faktury/`)
```
faktury/
├── api/                  # REST API implementation
│   ├── views.py         # API endpoints
│   ├── serializers.py   # Data serialization
│   ├── authentication.py # JWT auth logic
│   └── throttling.py    # Rate limiting
├── services/            # Business logic layer
│   ├── ocr_integration.py      # OCR orchestration
│   ├── polish_invoice_processor.py # Polish-specific processing
│   ├── confidence_calculator.py   # OCR confidence scoring
│   └── document_processor.py      # Document handling
├── views_modules/       # Modular view organization
│   ├── invoice_views.py # Invoice management
│   ├── ocr_views.py     # OCR processing views
│   └── auth_views.py    # Authentication views
├── templates/           # Django templates
├── static/              # App-specific static files
├── migrations/          # Database migrations
└── tests/               # Test suite
```

## Key Architecture Patterns

### Service Layer Pattern
Business logic is organized in `faktury/services/`:
- Each service handles a specific domain (OCR, invoices, etc.)
- Services are imported and used by views
- Promotes code reuse and testability

### Modular Views
Views are split into logical modules in `views_modules/`:
- `invoice_views.py` - Invoice CRUD operations
- `ocr_views.py` - OCR processing endpoints
- `auth_views.py` - Authentication logic
- Main `views.py` imports from modules

### API Organization
REST API follows DRF conventions:
- `api/views.py` - API viewsets and endpoints
- `api/serializers.py` - Request/response serialization
- `api/permissions.py` - Access control
- `api/throttling.py` - Rate limiting configuration

## File Naming Conventions

### Python Files
- `snake_case` for all Python files and modules
- Service classes: `SomethingService` (PascalCase)
- View classes: `SomethingView` or `SomethingViewSet`
- Model classes: `SomethingModel` (though often just `Something`)

### Templates
- `snake_case.html` for template files
- Organized by feature: `faktury/invoice_detail.html`
- Shared templates in root `templates/` directory

### Static Files
- `kebab-case.css` and `kebab-case.js` for static assets
- Organized by type: `css/`, `js/`, `images/`
- App-specific assets in `faktury/static/faktury/`

## Database Models
Located in `faktury/models.py` with key entities:
- `Faktura` - Invoice model with Polish fields
- `Kontrahent` - Contractor/client information
- `Firma` - Company/business entity
- `OCRResult` - OCR processing results
- `DocumentUpload` - File upload tracking

## Migration Strategy
- Migrations in `faktury/migrations/`
- OCR-related migrations prefixed with descriptive names
- Use descriptive migration names: `0021_add_ocr_fields_to_faktura.py`

## Testing Organization
```
faktury/tests/
├── test_ocr_integration.py      # OCR pipeline tests
├── test_api_views.py            # API endpoint tests
├── test_confidence_calculator.py # OCR confidence tests
└── test_*.py                    # Feature-specific tests
```

## Configuration Files
- `faktulove/settings.py` - Main Django settings
- `faktury_projekt/settings.py` - Alternative settings module
- `.env` - Environment variables
- `docker-compose.yml` - Development containers
- `requirements.txt` - Python dependencies

## Static Assets Organization
```
static/
├── assets/              # Third-party assets (Bootstrap, etc.)
├── css/                 # Custom stylesheets
├── js/                  # Custom JavaScript
└── images/              # Static images
```

## Media Files Structure
```
media/
├── ocr_uploads/         # OCR document uploads
│   └── 2025/           # Organized by year/month
├── documents/           # Generated documents
└── exports/             # Data export files
```

## Docker Structure
```
docker/
├── ocr-processor/       # OCR microservice container
│   ├── Dockerfile
│   └── healthcheck.sh
└── volumes/             # Persistent data volumes
    ├── ocr_models/      # OCR model cache
    └── ocr_temp/        # Temporary processing files
```

## Import Conventions
- Absolute imports preferred: `from faktury.services import OCRService`
- Service imports: `from faktury.services.ocr_integration import OCRIntegrationService`
- Model imports: `from faktury.models import Faktura, OCRResult`
- API imports: `from faktury.api.serializers import InvoiceSerializer`