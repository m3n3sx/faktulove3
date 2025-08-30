from faktulove.settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configure properly for your domain

# Security (configure for production)
SECURE_SSL_REDIRECT = False  # Set to True when SSL is configured
SESSION_COOKIE_SECURE = False  # Set to True when SSL is configured
CSRF_COOKIE_SECURE = False  # Set to True when SSL is configured

# Database connection pooling
if 'default' in DATABASES:
    DATABASES['default']['CONN_MAX_AGE'] = 60

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}

# OCR Production Settings
OCR_PROCESSING_TIMEOUT = 30
OCR_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
OCR_CONCURRENT_LIMIT = 50
OCR_RETRY_ATTEMPTS = 3
