# OCR Integration for FaktuLove

## Overview

This document describes the complete OCR integration system for FaktuLove, which automatically processes uploaded invoice documents and creates Faktura records based on extracted data.

## Architecture

### Components

1. **Models** (`faktury/models.py`)
   - `DocumentUpload`: Tracks uploaded documents
   - `OCRResult`: Stores OCR extraction results
   - `OCRValidation`: Manual validation tracking
   - `OCRProcessingLog`: Processing logs

2. **Services** (`faktury/services/ocr_integration.py`)
   - `OCRDataValidator`: Validates extracted OCR data
   - `FakturaCreator`: Creates Faktura from OCR data
   - Integration functions for processing

3. **Signals** (`faktury/signals.py`)
   - Automatic processing triggers
   - Status synchronization
   - Error handling

4. **Tasks** (`faktury/tasks.py`)
   - Celery tasks for async processing
   - Batch processing
   - Cleanup tasks

## Workflow

### 1. Document Upload
```
User uploads document → DocumentUpload created → OCR processing starts
```

### 2. OCR Processing
```
Document processed → OCRResult created → Automatic evaluation
```

### 3. Automatic Decision Making

Based on confidence score:

- **≥ 90%**: Auto-create Faktura
- **80-89%**: Mark as completed, no auto-creation
- **< 80%**: Require manual review

### 4. Faktura Creation
```
High confidence → Validate data → Create Kontrahent → Create Faktura → Create Positions
```

## Configuration

### Confidence Thresholds

The system uses these default thresholds:

```python
# In OCRResult model
def can_auto_create_faktura(self):
    return self.confidence_score >= 90.0

def needs_human_review(self):
    return self.confidence_score < 80.0
```

### OCR Data Format

Expected OCR extracted data structure:

```json
{
    "numer_faktury": "FV/001/2025",
    "data_wystawienia": "2025-01-15",
    "data_sprzedazy": "2025-01-15",
    "sprzedawca_nazwa": "Supplier Company",
    "sprzedawca_nip": "1234567890",
    "sprzedawca_ulica": "Supplier Street",
    "sprzedawca_numer_domu": "10",
    "sprzedawca_kod_pocztowy": "11-111",
    "sprzedawca_miejscowosc": "Supplier City",
    "nabywca_nazwa": "Buyer Company",
    "pozycje": [
        {
            "nazwa": "Product Name",
            "ilosc": "2.00",
            "jednostka": "szt",
            "cena_netto": "50.00",
            "vat": "23"
        }
    ],
    "suma_brutto": "123.00",
    "sposob_platnosci": "przelew",
    "termin_platnosci_dni": 14
}
```

## Usage

### Automatic Processing

OCR results are processed automatically when created:

```python
# OCRResult.save() method triggers processing
ocr_result = OCRResult.objects.create(
    document=document,
    extracted_data=ocr_data,
    confidence_score=95.0,
    processing_time=2.5
)
# Processing starts automatically
```

### Manual Processing

For manual review cases:

```python
from faktury.services.ocr_integration import create_faktura_from_ocr_manual

faktura = create_faktura_from_ocr_manual(ocr_result_id, user)
```

### Batch Processing

Process all pending OCR results:

```python
from faktury.tasks import batch_process_pending_ocr_results

# Via Celery
batch_process_pending_ocr_results.delay()

# Or via management command
python manage.py test_ocr_integration --process-pending
```

## API Integration

### Processing Status

Check OCR result status:

```python
ocr_result = OCRResult.objects.get(id=ocr_result_id)

print(f"Status: {ocr_result.get_processing_status_display()}")
print(f"Confidence: {ocr_result.confidence_score}%")
print(f"Needs review: {ocr_result.needs_human_review}")
print(f"Can auto-create: {ocr_result.can_auto_create_faktura}")

if ocr_result.faktura:
    print(f"Created Faktura: {ocr_result.faktura.numer}")
```

### Statistics

Get processing statistics:

```python
from faktury.services.ocr_integration import get_ocr_processing_stats

stats = get_ocr_processing_stats(user)
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Manual review rate: {stats['manual_review_rate']:.1f}%")
```

## Error Handling

### Validation Errors

OCR data is validated before Faktura creation:

```python
from faktury.services.ocr_integration import OCRDataValidator

is_valid, errors = OCRDataValidator.validate_ocr_data(extracted_data)
if not is_valid:
    print("Validation errors:", errors)
```

### Processing Errors

Failed processing is logged and tracked:

```python
# OCR result marked as failed
ocr_result.processing_status == 'failed'
print(f"Error: {ocr_result.error_message}")
```

### Retry Mechanism

Celery tasks include retry logic:

```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_ocr_result_task(self, ocr_result_id):
    # Automatic retry on failure
    pass
```

## Database Schema

### New Fields in Faktura

```sql
-- OCR integration fields
source_document_id INTEGER REFERENCES faktury_documentupload(id),
ocr_confidence FLOAT CHECK (ocr_confidence >= 0.0 AND ocr_confidence <= 100.0),
manual_verification_required BOOLEAN DEFAULT FALSE,
ocr_processing_time FLOAT CHECK (ocr_processing_time >= 0.0),
ocr_extracted_at TIMESTAMP
```

### OCRResult Model

```sql
-- Core fields
document_id INTEGER REFERENCES faktury_documentupload(id),
faktura_id INTEGER REFERENCES faktury_faktura(id),
raw_text TEXT,
extracted_data JSONB,
confidence_score FLOAT,
processing_time FLOAT,

-- Status tracking
processing_status VARCHAR(20) DEFAULT 'pending',
error_message TEXT,
auto_created_faktura BOOLEAN DEFAULT FALSE,

-- Metadata
field_confidence JSONB DEFAULT '{}',
processor_version VARCHAR(50),
processing_location VARCHAR(50)
```

## Performance Optimization

### Indexes

Key indexes for OCR queries:

```sql
-- Individual indexes
CREATE INDEX faktury_faktura_ocr_confidence_idx ON faktury_faktura (ocr_confidence);
CREATE INDEX faktury_faktura_manual_verification_idx ON faktury_faktura (manual_verification_required);

-- Compound indexes
CREATE INDEX faktury_faktura_user_ocr_confidence_idx ON faktury_faktura (user_id, ocr_confidence);
CREATE INDEX faktury_ocrresult_processing_status_idx ON faktury_ocrresult (processing_status);
```

### Query Optimization

Efficient queries for common operations:

```python
# Find invoices requiring manual verification
invoices_to_review = Faktura.objects.filter(
    user=user,
    manual_verification_required=True
).select_related('source_document', 'nabywca')

# Find high-confidence auto-created invoices
auto_created = Faktura.objects.filter(
    user=user,
    ocr_confidence__gte=90.0,
    source_document__isnull=False
)
```

## Testing

### Unit Tests

Run OCR integration tests:

```bash
python manage.py test faktury.tests.test_ocr_integration
```

### Management Command

Test integration with sample data:

```bash
# Create test data
python manage.py test_ocr_integration --create-test-data

# Process pending results
python manage.py test_ocr_integration --process-pending

# Show statistics
python manage.py test_ocr_integration --stats

# Process specific result
python manage.py test_ocr_integration --ocr-result-id 123
```

## Monitoring

### Logging

OCR processing is logged at various levels:

```python
import logging
logger = logging.getLogger(__name__)

# Key log messages
logger.info(f"Processing OCR result {ocr_result_id}")
logger.info(f"Auto-created Faktura {faktura.numer}")
logger.warning(f"OCR result requires manual review")
logger.error(f"OCR processing failed: {error}")
```

### Metrics

Track key metrics:

- Processing success rate
- Average confidence scores
- Manual review rate
- Processing time distribution
- Error rates by error type

### Celery Monitoring

Monitor async tasks:

```bash
# Check task status
celery -A your_project inspect active

# Monitor task results
celery -A your_project events
```

## Deployment

### Migration Steps

1. Apply database migrations:
```bash
python manage.py migrate faktury 0024
```

2. Update model definitions (already done in models.py)

3. Connect signals (handled in apps.py)

4. Configure Celery for async processing

### Configuration

Add to Django settings:

```python
# OCR Integration Settings
OCR_SETTINGS = {
    'confidence_thresholds': {
        'auto_approve': 90.0,
        'review_required': 80.0,
    },
    'processing': {
        'async_enabled': True,
        'retry_attempts': 3,
        'retry_delay': 60,
    }
}

# Celery configuration
CELERY_TASK_ROUTES = {
    'faktury.tasks.process_ocr_result_task': {'queue': 'ocr_processing'},
}
```

## Troubleshooting

### Common Issues

1. **OCR results not processing**
   - Check Celery is running
   - Verify signals are connected
   - Check for validation errors

2. **Faktura creation fails**
   - Verify user has associated Firma
   - Check OCR data format
   - Review validation errors

3. **Performance issues**
   - Check database indexes
   - Monitor Celery queue length
   - Review query patterns

### Debug Commands

```bash
# Check OCR result status
python manage.py shell
>>> from faktury.models import OCRResult
>>> ocr = OCRResult.objects.get(id=123)
>>> print(f"Status: {ocr.processing_status}")
>>> print(f"Error: {ocr.error_message}")

# Manual processing
>>> from faktury.services.ocr_integration import process_ocr_result
>>> faktura = process_ocr_result(123)
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Confidence score calibration
   - Field-specific confidence tracking
   - Learning from manual corrections

2. **Advanced Validation**
   - Cross-field validation rules
   - Business logic validation
   - Duplicate detection

3. **User Interface**
   - OCR result review interface
   - Batch approval workflows
   - Processing status dashboard

4. **Integration Improvements**
   - Multiple OCR provider support
   - Real-time processing status
   - Advanced error recovery

### API Extensions

Future API endpoints:

```python
# OCR processing status
GET /api/ocr-results/{id}/status/

# Manual review interface
GET /api/ocr-results/pending-review/
POST /api/ocr-results/{id}/approve/
POST /api/ocr-results/{id}/reject/

# Batch operations
POST /api/ocr-results/batch-process/
GET /api/ocr-results/statistics/
```

---

## Support

For issues or questions about OCR integration:

1. Check the logs for error messages
2. Run the test management command
3. Review the unit tests for usage examples
4. Contact the development team

**Last Updated**: January 2025  
**Version**: 1.0.0