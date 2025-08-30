"""
Staging Environment Configuration for Design System Integration
Provides staging-specific settings and configurations
"""

import os
from pathlib import Path
from .settings import *

# Staging environment identification
ENVIRONMENT = 'staging'
DEBUG = False
ALLOWED_HOSTS = [
    'staging.faktulove.local',
    'staging-faktulove.herokuapp.com',
    '127.0.0.1',
    'localhost'
]

# Database configuration for staging
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('STAGING_DB_NAME', 'faktulove_staging'),
        'USER': os.environ.get('STAGING_DB_USER', 'faktulove_staging'),
        'PASSWORD': os.environ.get('STAGING_DB_PASSWORD'),
        'HOST': os.environ.get('STAGING_DB_HOST', 'localhost'),
        'PORT': os.environ.get('STAGING_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Redis configuration for staging
REDIS_URL = os.environ.get('STAGING_REDIS_URL', 'redis://localhost:6379/1')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery configuration for staging
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Static files configuration for staging
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_staging')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration for staging
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_staging')

# Design System specific settings for staging
DESIGN_SYSTEM_CONFIG = {
    'ENVIRONMENT': 'staging',
    'DEBUG_MODE': True,
    'PERFORMANCE_MONITORING': True,
    'VISUAL_REGRESSION_TESTING': True,
    'ACCESSIBILITY_TESTING': True,
    'POLISH_BUSINESS_VALIDATION': True,
    
    # Component settings
    'COMPONENTS': {
        'LAZY_LOADING': True,
        'CODE_SPLITTING': True,
        'TREE_SHAKING': True,
        'BUNDLE_ANALYSIS': True
    },
    
    # Theme settings
    'THEMES': {
        'DEFAULT_THEME': 'light',
        'AVAILABLE_THEMES': ['light', 'dark', 'polish-business'],
        'THEME_PERSISTENCE': True,
        'CUSTOM_THEMES': True
    },
    
    # Polish business settings
    'POLISH_BUSINESS': {
        'NIP_VALIDATION': True,
        'VAT_RATES': [0, 5, 8, 23],
        'CURRENCY': 'PLN',
        'DATE_FORMAT': 'DD.MM.YYYY',
        'COMPLIANCE_CHECKING': True
    },
    
    # Performance settings
    'PERFORMANCE': {
        'CORE_WEB_VITALS_MONITORING': True,
        'BUNDLE_SIZE_MONITORING': True,
        'COMPONENT_PERFORMANCE_TRACKING': True,
        'MEMORY_USAGE_MONITORING': True
    },
    
    # Testing settings
    'TESTING': {
        'VISUAL_REGRESSION': True,
        'ACCESSIBILITY_AUTOMATION': True,
        'PERFORMANCE_BENCHMARKS': True,
        'CROSS_BROWSER_TESTING': True
    }
}

# Logging configuration for staging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'staging.log'),
            'formatter': 'verbose',
        },
        'design_system_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'design_system_staging.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'faktury.design_system': {
            'handlers': ['design_system_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'faktury.polish_business': {
            'handlers': ['design_system_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security settings for staging
SECRET_KEY = os.environ.get('STAGING_SECRET_KEY')
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings for staging frontend
CORS_ALLOWED_ORIGINS = [
    "http://staging.faktulove.local",
    "https://staging.faktulove.local",
    "http://localhost:3000",  # For development frontend
]

CORS_ALLOW_CREDENTIALS = True

# Email configuration for staging
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('STAGING_EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('STAGING_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('STAGING_EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'FaktuLove Staging <staging@faktulove.local>'

# OCR configuration for staging
OCR_CONFIG = {
    'ENGINES': ['tesseract', 'easyocr'],
    'DEFAULT_ENGINE': 'tesseract',
    'FALLBACK_ENGINE': 'easyocr',
    'CONFIDENCE_THRESHOLD': 0.7,
    'POLISH_LANGUAGE_SUPPORT': True,
    'PREPROCESSING': True,
    'RESULT_CACHING': True,
    'PERFORMANCE_MONITORING': True
}

# API configuration for staging
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'design_system': '500/hour',
        'polish_business': '200/hour'
    }
})

# Monitoring and analytics for staging
MONITORING_CONFIG = {
    'PERFORMANCE_MONITORING': True,
    'ERROR_TRACKING': True,
    'USER_ANALYTICS': True,
    'DESIGN_SYSTEM_METRICS': True,
    'POLISH_BUSINESS_METRICS': True,
    
    'SENTRY_DSN': os.environ.get('STAGING_SENTRY_DSN'),
    'GOOGLE_ANALYTICS_ID': os.environ.get('STAGING_GA_ID'),
    
    'CUSTOM_METRICS': {
        'COMPONENT_USAGE': True,
        'THEME_SWITCHING': True,
        'ACCESSIBILITY_USAGE': True,
        'POLISH_BUSINESS_USAGE': True
    }
}

# Feature flags for staging
FEATURE_FLAGS = {
    'DESIGN_SYSTEM_INTEGRATION': True,
    'POLISH_BUSINESS_COMPONENTS': True,
    'ADVANCED_THEMING': True,
    'ACCESSIBILITY_FEATURES': True,
    'PERFORMANCE_MONITORING': True,
    'VISUAL_REGRESSION_TESTING': True,
    'USER_ACCEPTANCE_TESTING': True,
    
    # Gradual rollout flags
    'NEW_INVOICE_FORM': True,
    'NEW_OCR_INTERFACE': True,
    'NEW_DASHBOARD': True,
    'NEW_AUTH_PAGES': True
}

# Testing configuration for staging
TESTING_CONFIG = {
    'UNIT_TESTS': True,
    'INTEGRATION_TESTS': True,
    'E2E_TESTS': True,
    'VISUAL_REGRESSION_TESTS': True,
    'ACCESSIBILITY_TESTS': True,
    'PERFORMANCE_TESTS': True,
    'POLISH_BUSINESS_TESTS': True,
    
    'TEST_DATA_FIXTURES': True,
    'MOCK_EXTERNAL_SERVICES': True,
    'PARALLEL_TESTING': True,
    'COVERAGE_REPORTING': True
}

# Deployment configuration
DEPLOYMENT_CONFIG = {
    'ENVIRONMENT': 'staging',
    'VERSION': os.environ.get('DESIGN_SYSTEM_VERSION', '1.0.0'),
    'DEPLOYMENT_ID': os.environ.get('DEPLOYMENT_ID'),
    'ROLLBACK_ENABLED': True,
    'HEALTH_CHECKS': True,
    'SMOKE_TESTS': True,
    'PERFORMANCE_VALIDATION': True
}

# Add design system apps to INSTALLED_APPS
INSTALLED_APPS += [
    'faktury.design_system',
    'faktury.polish_business',
    'faktury.monitoring',
    'faktury.testing'
]

# Middleware for staging
MIDDLEWARE += [
    'faktury.middleware.DesignSystemMiddleware',
    'faktury.middleware.PolishBusinessMiddleware',
    'faktury.middleware.PerformanceMonitoringMiddleware',
    'faktury.middleware.StagingSecurityMiddleware'
]

# Template context processors for design system
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'faktury.context_processors.design_system_context',
    'faktury.context_processors.polish_business_context',
    'faktury.context_processors.theme_context'
]

# Internationalization for Polish business
LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('pl', 'Polski'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Polish business specific settings
POLISH_BUSINESS_CONFIG = {
    'VAT_RATES': [0, 5, 8, 23],
    'DEFAULT_VAT_RATE': 23,
    'CURRENCY': 'PLN',
    'CURRENCY_SYMBOL': 'zł',
    'DATE_FORMAT': 'j.n.Y',
    'DATETIME_FORMAT': 'j.n.Y H:i',
    'DECIMAL_SEPARATOR': ',',
    'THOUSAND_SEPARATOR': ' ',
    'NIP_VALIDATION': True,
    'REGON_VALIDATION': True,
    'KRS_VALIDATION': True
}

print(f"Staging environment configuration loaded for Design System Integration v{DEPLOYMENT_CONFIG['VERSION']}")