# PaddleOCR Integration Guide

## Overview

This guide provides comprehensive instructions for setting up, configuring, and using PaddleOCR as the primary OCR engine in the FaktuLove Polish invoice management system. PaddleOCR has been implemented to achieve >90% accuracy on Polish invoices through specialized preprocessing, pattern recognition, and confidence scoring algorithms.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Configuration](#configuration)
3. [Polish Pattern Configuration](#polish-pattern-configuration)
4. [Performance Tuning](#performance-tuning)
5. [Troubleshooting](#troubleshooting)
6. [API Usage](#api-usage)
7. [Monitoring and Debugging](#monitoring-and-debugging)

## Installation and Setup

### Prerequisites

- Python 3.11+
- Django 4.2.23+
- At least 2GB RAM available for OCR processing
- Optional: CUDA-compatible GPU for acceleration

### Basic Installation

1. **Install PaddleOCR dependencies:**
```bash
pip install paddlepaddle paddleocr
```

2. **Download Polish language models:**
```bash
python -c "
import paddleocr
# This will download Polish models to ~/.paddleocr/
ocr = paddleocr.PaddleOCR(lang='pl')
"
```

3. **Set up model directory:**
```bash
mkdir -p /app/paddle_models
export PADDLEOCR_MODEL_DIR=/app/paddle_models
```

### Docker Installation

Add to your Dockerfile:
```dockerfile
# Install PaddleOCR
RUN pip install paddlepaddle paddleocr

# Create model directory
RUN mkdir -p /app/paddle_models

# Download Polish models during build
RUN python -c "import paddleocr; paddleocr.PaddleOCR(lang='pl')"

# Set environment variables
ENV PADDLEOCR_MODEL_DIR=/app/paddle_models
ENV PADDLEOCR_ENABLED=true
```

### GPU Support (Optional)

For GPU acceleration:
```bash
# Install GPU version of PaddlePaddle
pip install paddlepaddle-gpu

# Verify GPU availability
python -c "
import paddle
print('GPU available:', paddle.is_compiled_with_cuda())
print('GPU count:', paddle.device.cuda.device_count())
"
```

## Configuration

### Django Settings

Add to your `settings.py`:

```python
# PaddleOCR Configuration
PADDLEOCR_CONFIG = {
    'enabled': True,
    'languages': ['pl', 'en'],
    'use_gpu': False,  # Set to True if GPU available
    'model_dir': os.environ.get('PADDLEOCR_MODEL_DIR', '/app/paddle_models/'),
    'det_model_name': 'pl_PP-OCRv4_det',
    'rec_model_name': 'pl_PP-OCRv4_rec',
    'cls_model_name': 'ch_ppocr_mobile_v2.0_cls',
    'max_text_length': 25000,
    'use_angle_cls': True,
    'use_space_char': True,
    'drop_score': 0.5,
    'preprocessing': {
        'enabled': True,
        'noise_reduction': True,
        'contrast_enhancement': True,
        'skew_correction': True,
        'resolution_optimization': True
    },
    'polish_optimization': {
        'enabled': True,
        'nip_validation': True,
        'date_format_enhancement': True,
        'currency_parsing': True,
        'spatial_analysis': True
    },
    'performance': {
        'max_memory_mb': 800,
        'timeout_seconds': 10,
        'max_workers': 2,
        'batch_size': 1
    }
}

# OCR Engine Priority (PaddleOCR first)
OCR_ENGINE_PRIORITY = ['paddleocr', 'tesseract', 'easyocr']

# Feature Flags
OCR_FEATURE_FLAGS = {
    'use_paddleocr': True,
    'paddleocr_primary': True,
    'enable_gpu_acceleration': False,
    'advanced_preprocessing': True,
    'polish_pattern_enhancement': True
}
```

### Environment Variables

Create or update your `.env` file:

```bash
# PaddleOCR Configuration
PADDLEOCR_ENABLED=true
PADDLEOCR_USE_GPU=false
PADDLEOCR_MODEL_DIR=/app/paddle_models
PADDLEOCR_LANGUAGES=pl,en
PADDLEOCR_MAX_MEMORY=800

# Performance Tuning
PADDLEOCR_MAX_WORKERS=2
PADDLEOCR_TIMEOUT=10
PADDLEOCR_BATCH_SIZE=1

# Debug Settings
PADDLEOCR_DEBUG=false
PADDLEOCR_LOG_LEVEL=INFO
```

## Polish Pattern Configuration

### NIP (Tax Identification Number) Validation

The system includes comprehensive NIP validation with checksum verification:

```python
# Example NIP patterns recognized:
# - 1234567890 (10 digits)
# - 123-456-78-90 (with dashes)
# - 123 456 78 90 (with spaces)
# - PL1234567890 (with country prefix)

# Checksum validation algorithm implemented
# Invalid NIPs are flagged for manual review
```

### REGON and KRS Numbers

```python
# REGON patterns (9 or 14 digits):
# - 123456789
# - 12345678901234

# KRS patterns (10 digits):
# - 0000123456
```

### Polish Date Formats

Supported date formats:
- `DD.MM.YYYY` (e.g., 15.01.2024)
- `DD-MM-YYYY` (e.g., 15-01-2024)
- `DD/MM/YYYY` (e.g., 15/01/2024)
- `YYYY-MM-DD` (ISO format)

### VAT Rates

Polish VAT rates automatically recognized:
- 0% (zero-rated)
- 5% (reduced rate)
- 8% (reduced rate)
- 23% (standard rate)

### Currency Formats

Supported Polish currency formats:
- `1 234,56 zł` (Polish format with spaces)
- `1.234,56 PLN` (with thousand separators)
- `1234.56` (decimal point format)
- `1234,56` (decimal comma format)

## Performance Tuning

### Memory Optimization

1. **Adjust memory limits:**
```python
PADDLEOCR_CONFIG['performance']['max_memory_mb'] = 1024  # Increase if needed
```

2. **Monitor memory usage:**
```bash
# Check memory usage during processing
python manage.py shell -c "
from faktury.services.paddle_ocr_service import PaddleOCRService
service = PaddleOCRService()
print('Memory usage:', service.get_memory_usage())
"
```

### Processing Speed Optimization

1. **Enable GPU acceleration (if available):**
```python
PADDLEOCR_CONFIG['use_gpu'] = True
OCR_FEATURE_FLAGS['enable_gpu_acceleration'] = True
```

2. **Adjust preprocessing settings:**
```python
# Disable heavy preprocessing for speed
PADDLEOCR_CONFIG['preprocessing']['noise_reduction'] = False
PADDLEOCR_CONFIG['preprocessing']['contrast_enhancement'] = False
```

3. **Optimize batch processing:**
```python
PADDLEOCR_CONFIG['performance']['batch_size'] = 4  # Process multiple images
PADDLEOCR_CONFIG['performance']['max_workers'] = 4  # Increase workers
```

### Quality vs Speed Trade-offs

**High Quality (Slower):**
```python
PADDLEOCR_CONFIG.update({
    'drop_score': 0.3,  # Lower threshold for better recall
    'preprocessing': {
        'enabled': True,
        'noise_reduction': True,
        'contrast_enhancement': True,
        'skew_correction': True,
        'resolution_optimization': True
    }
})
```

**High Speed (Lower Quality):**
```python
PADDLEOCR_CONFIG.update({
    'drop_score': 0.7,  # Higher threshold for speed
    'preprocessing': {
        'enabled': False  # Disable preprocessing
    }
})
```

## Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Problem:** `PaddleOCRModelError: Failed to load Polish models`

**Solution:**
```bash
# Re-download models
rm -rf ~/.paddleocr/
python -c "import paddleocr; paddleocr.PaddleOCR(lang='pl')"

# Check model directory permissions
chmod -R 755 /app/paddle_models/
```

#### 2. Memory Issues

**Problem:** `MemoryError: Cannot allocate memory for OCR processing`

**Solutions:**
```python
# Reduce memory usage
PADDLEOCR_CONFIG['performance']['max_memory_mb'] = 512
PADDLEOCR_CONFIG['performance']['batch_size'] = 1

# Enable memory monitoring
PADDLEOCR_CONFIG['debug'] = True
```

#### 3. Processing Timeouts

**Problem:** OCR processing takes too long

**Solutions:**
```python
# Increase timeout
PADDLEOCR_CONFIG['performance']['timeout_seconds'] = 30

# Reduce image resolution
PADDLEOCR_CONFIG['preprocessing']['resolution_optimization'] = True
```

#### 4. Low Accuracy on Polish Text

**Problem:** Poor recognition of Polish characters

**Solutions:**
```python
# Ensure Polish language is enabled
PADDLEOCR_CONFIG['languages'] = ['pl', 'en']

# Enable Polish optimizations
PADDLEOCR_CONFIG['polish_optimization']['enabled'] = True

# Check model versions
python -c "
import paddleocr
ocr = paddleocr.PaddleOCR(lang='pl')
print('Model info:', ocr.text_recognizer.character_dict_path)
"
```

### Debug Mode

Enable debug mode for detailed logging:

```python
# In settings.py
PADDLEOCR_CONFIG['debug'] = True
LOGGING['loggers']['faktury.services.paddle_ocr_service'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}
```

### Performance Benchmarking

Run performance tests:

```bash
# Run PaddleOCR benchmarks
python manage.py test faktury.tests.test_paddle_ocr_performance

# Generate performance report
python -c "
from faktury.services.paddle_ocr_service import PaddleOCRService
service = PaddleOCRService()
report = service.generate_performance_report()
print(report)
"
```

## API Usage

### Basic Usage

```python
from faktury.services.paddle_ocr_service import PaddleOCRService

# Initialize service
ocr_service = PaddleOCRService()

# Process invoice
with open('invoice.pdf', 'rb') as f:
    result = ocr_service.process_invoice(f.read(), 'application/pdf')

print(f"Confidence: {result['confidence_score']}")
print(f"Invoice number: {result['extracted_data']['numer_faktury']}")
print(f"NIP: {result['extracted_data']['sprzedawca_nip']}")
```

### Advanced Usage with Custom Configuration

```python
from faktury.services.paddle_ocr_service import PaddleOCRService

# Custom configuration
config = {
    'languages': ['pl'],
    'use_gpu': True,
    'drop_score': 0.4,
    'preprocessing': {
        'enabled': True,
        'noise_reduction': True,
        'contrast_enhancement': True
    }
}

# Initialize with custom config
ocr_service = PaddleOCRService(**config)

# Process with confidence threshold
result = ocr_service.process_invoice(
    file_content=pdf_bytes,
    mime_type='application/pdf',
    min_confidence=0.8
)

if result['confidence_score'] >= 0.8:
    print("High confidence result")
else:
    print("Manual review required")
```

### Integration with OCR Service Factory

```python
from faktury.services.ocr_service_factory import OCRServiceFactory

# Get PaddleOCR service through factory
ocr_service = OCRServiceFactory.get_service('paddleocr')

# Process document
result = ocr_service.process_invoice(file_content, mime_type)
```

## Monitoring and Debugging

### Health Checks

```python
# Check PaddleOCR service health
from faktury.services.paddle_ocr_service import PaddleOCRService

service = PaddleOCRService()
health = service.health_check()

print(f"Service status: {health['status']}")
print(f"Models loaded: {health['models_loaded']}")
print(f"Memory usage: {health['memory_usage_mb']}MB")
print(f"GPU available: {health['gpu_available']}")
```

### Performance Metrics

```python
# Get performance statistics
stats = service.get_performance_stats()

print(f"Average processing time: {stats['avg_processing_time']}s")
print(f"Success rate: {stats['success_rate']}%")
print(f"Average confidence: {stats['avg_confidence']}")
```

### Error Monitoring

```python
# Monitor errors and fallbacks
error_stats = service.get_error_statistics()

print(f"Total errors: {error_stats['total_errors']}")
print(f"Fallback activations: {error_stats['fallback_count']}")
print(f"Most common errors: {error_stats['common_errors']}")
```

### Logging Configuration

Add to your Django logging configuration:

```python
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
        'paddle_ocr_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/paddle_ocr.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'faktury.services.paddle_ocr_service': {
            'handlers': ['paddle_ocr_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Best Practices

### 1. Resource Management

- Monitor memory usage regularly
- Set appropriate timeouts for processing
- Use GPU acceleration when available
- Implement proper cleanup of temporary files

### 2. Error Handling

- Always implement fallback mechanisms
- Log errors with sufficient detail for debugging
- Use confidence thresholds for quality control
- Implement retry logic for transient failures

### 3. Performance Optimization

- Batch process multiple documents when possible
- Cache models in memory for repeated use
- Optimize image preprocessing based on document quality
- Monitor and tune performance parameters regularly

### 4. Quality Assurance

- Validate extracted data using business rules
- Implement confidence-based review workflows
- Regular testing with diverse document samples
- Monitor accuracy metrics over time

## Support and Maintenance

### Regular Maintenance Tasks

1. **Model Updates:**
```bash
# Check for model updates monthly
python -c "
import paddleocr
# This will download latest models if available
ocr = paddleocr.PaddleOCR(lang='pl', show_log=True)
"
```

2. **Performance Monitoring:**
```bash
# Weekly performance check
python manage.py paddle_ocr_health_check
python manage.py paddle_ocr_performance_report
```

3. **Log Rotation:**
```bash
# Rotate PaddleOCR logs
logrotate /etc/logrotate.d/paddle_ocr
```

### Getting Help

- **Documentation:** Check this guide and inline code documentation
- **Logs:** Review `/logs/paddle_ocr.log` for detailed error information
- **Health Checks:** Use built-in health check endpoints
- **Performance Reports:** Generate regular performance reports
- **Test Suite:** Run comprehensive test suite for validation

### Version Compatibility

| PaddleOCR Version | FaktuLove Version | Python Version | Notes |
|-------------------|-------------------|----------------|-------|
| 2.7.x | 1.0+ | 3.11+ | Recommended |
| 2.6.x | 1.0+ | 3.9+ | Supported |
| 2.5.x | 1.0+ | 3.8+ | Legacy support |

For the most up-to-date compatibility information, check the project requirements.txt file.