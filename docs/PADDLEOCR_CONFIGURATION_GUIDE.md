# PaddleOCR Configuration Guide

This document explains the PaddleOCR configuration settings added to the Django project.

## Overview

PaddleOCR has been integrated as the primary OCR engine for the FaktuLove system with comprehensive configuration options for performance tuning, Polish language optimization, and production deployment.

## Configuration Structure

### 1. Core Settings (`PADDLEOCR_CONFIG`)

Located in `faktulove/settings.py`, this contains all PaddleOCR-specific settings:

```python
PADDLEOCR_CONFIG = {
    'enabled': True,
    'languages': ['pl', 'en'],
    'use_gpu': False,
    'model_dir': '/app/paddle_models',
    # ... additional settings
}
```

### 2. Feature Flags (`OCR_FEATURE_FLAGS`)

Controls which PaddleOCR features are enabled:

```python
OCR_FEATURE_FLAGS = {
    'use_paddleocr': True,
    'paddleocr_primary': True,
    'enable_gpu_acceleration': False,
    'advanced_preprocessing': True,
    'polish_pattern_enhancement': True,
    # ... additional flags
}
```

### 3. Performance Configuration (`PADDLEOCR_PERFORMANCE_CONFIG`)

Optimizes PaddleOCR for production workloads:

```python
PADDLEOCR_PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 3,
    'memory_pool_size': 512,
    'enable_batch_processing': False,
    # ... additional performance settings
}
```

## Environment Variables

All configuration can be controlled via environment variables. Key variables include:

### Core Configuration
- `PADDLEOCR_ENABLED`: Enable/disable PaddleOCR (default: True)
- `PADDLEOCR_PRIMARY`: Use PaddleOCR as primary engine (default: True)
- `PADDLEOCR_MODEL_DIR`: Directory for PaddleOCR models
- `PADDLEOCR_LANGUAGES`: Comma-separated list of languages (default: pl,en)

### Performance Tuning
- `PADDLEOCR_MAX_MEMORY`: Maximum memory usage in MB (default: 800)
- `PADDLEOCR_MAX_WORKERS`: Number of worker processes (default: 2)
- `PADDLEOCR_TIMEOUT`: Processing timeout in seconds (default: 30)
- `PADDLEOCR_USE_GPU`: Enable GPU acceleration (default: False)

### Polish Optimization
- `PADDLEOCR_POLISH_OPTIMIZATION`: Enable Polish-specific features (default: True)
- `PADDLEOCR_NIP_VALIDATION`: Enable NIP validation (default: True)
- `PADDLEOCR_CURRENCY_PARSING`: Enable Polish currency parsing (default: True)

### Memory Management
- `PADDLEOCR_MEMORY_MAX`: Maximum memory limit in MB
- `PADDLEOCR_MEMORY_WARNING`: Warning threshold in MB
- `PADDLEOCR_MEMORY_CRITICAL`: Critical threshold in MB

### Timeout Configuration
- `PADDLEOCR_TIMEOUT_INIT`: Initialization timeout
- `PADDLEOCR_TIMEOUT_PROCESSING`: Processing timeout
- `PADDLEOCR_TIMEOUT_MODEL_LOADING`: Model loading timeout

## Validation

The configuration includes built-in validation:

### Automatic Validation
- Runs on Django startup if `VALIDATE_OCR_CONFIG=True`
- Validates all configuration parameters
- Checks memory thresholds and timeout values
- Verifies model directory existence

### Manual Validation
Run the management command to validate configuration:

```bash
python manage.py validate_ocr_config
```

This will show:
- Configuration errors and warnings
- Current settings summary
- Feature flag status
- Engine priority order

## Engine Priority

PaddleOCR is configured as the primary engine in the priority order:

```python
OCR_ENGINE_PRIORITY = [
    'paddleocr',    # Primary engine
    'tesseract',    # Secondary fallback
    'easyocr',      # Tertiary fallback
    'google'        # Final fallback (if enabled)
]
```

## Logging

PaddleOCR has dedicated logging configuration:

- Service logs: `faktury.services.paddle_ocr_service`
- Engine logs: `faktury.services.paddle_ocr_engine`
- Polish processor logs: `faktury.services.enhanced_polish_processor`
- Confidence calculator logs: `faktury.services.paddle_confidence_calculator`

Log level can be controlled with `PADDLEOCR_LOGGING_LEVEL` environment variable.

## Celery Integration

PaddleOCR tasks are routed to dedicated queues:

- `paddleocr`: Main processing queue
- `paddleocr_batch`: Batch processing queue
- `paddleocr_maintenance`: Model warmup and maintenance
- `monitoring`: Performance monitoring tasks

## Throttling

API throttling is configured for PaddleOCR endpoints:

- `paddleocr_upload`: 8 requests per minute
- `paddleocr_process`: 15 requests per minute
- `paddleocr_batch`: 3 requests per minute
- `paddleocr_heavy`: 5 requests per minute (large files)

## Production Deployment

### Environment Setup

1. Copy `.env.example` to `.env`
2. Configure PaddleOCR-specific variables
3. Set appropriate memory limits for your server
4. Configure model directory path
5. Enable GPU if available

### Model Management

- Models are automatically downloaded on first use
- Model directory should be persistent across deployments
- Consider pre-downloading models in Docker builds

### Performance Monitoring

- Enable performance monitoring with `PADDLEOCR_PERFORMANCE_MONITORING=True`
- Monitor memory usage and processing times
- Use the validation command to check configuration

### Security

- All PaddleOCR processing respects existing OCR security settings
- File validation and size limits apply
- Audit logging is integrated with existing OCR audit system

## Troubleshooting

### Common Issues

1. **Model Directory Not Found**
   - Ensure `PADDLEOCR_MODEL_DIR` points to existing directory
   - Check directory permissions
   - Models will be downloaded automatically if directory is writable

2. **Memory Issues**
   - Reduce `PADDLEOCR_MAX_MEMORY` setting
   - Decrease `PADDLEOCR_MAX_WORKERS`
   - Enable memory optimization features

3. **Timeout Issues**
   - Increase `PADDLEOCR_TIMEOUT` values
   - Enable timeout degradation
   - Check system resources

4. **GPU Issues**
   - Verify CUDA installation if using GPU
   - Check PaddlePaddle GPU support
   - Fall back to CPU mode if needed

### Validation Command

Use the validation command to diagnose issues:

```bash
python manage.py validate_ocr_config --json
```

This provides detailed information about configuration status and any issues.

## Migration from Other OCR Engines

The configuration maintains compatibility with existing OCR systems:

- Existing API endpoints continue to work
- OCR results use the same database models
- Fallback to other engines is automatic
- Feature flags allow gradual rollout

## Support

For configuration issues:

1. Run the validation command
2. Check Django logs for PaddleOCR-specific messages
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed