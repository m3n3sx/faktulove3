import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-!vtvq(lht)_avs0e7t7pkf(=-2u=z68ej50pq_li$u0hfjlacn')
GUS_API_KEY = os.getenv('GUS_API_KEY', 'a44eade9e2ba46e9bec1')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Force DEBUG mode for development

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://app.ooxo.pl,https://faktulove.pl').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # Potrzebne dla django-allauth
    'faktury.apps.FakturyConfig',
    'allauth',  # Dodaj django-allauth
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # Dodaj providera Google
    'allauth.socialaccount.providers.facebook',
    'crispy_forms',  # Correct order
    'crispy_bootstrap5', # Correct order
    'import_export',
    'widget_tweaks',
    'django.contrib.humanize',
    #'notifications',
    
    # OCR and API additions
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'django_celery_results',
    'django_celery_beat',
    'drf_spectacular',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'faktury.middleware.SecurityHeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'faktury.api.responses.APIResponseMiddleware',  # Add API response middleware
    'faktury.api.logging_config.APIRequestLoggingMiddleware',  # Add API logging middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'faktury.middleware.FirmaCheckMiddleware',
]

ROOT_URLCONF = 'faktulove.urls'

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),  # Ogólny katalog
            os.path.join(BASE_DIR, "faktury", "templates"),  # Katalog w aplikacji faktury
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'faktury_projekt.wsgi.application'

# ignorowanie komunikatu ostrzeżenia z bazy danych.

SILENCED_SYSTEM_CHECKS = ['models.W036']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', ''),
        'PORT': os.getenv('DATABASE_PORT', ''),
        'OPTIONS': {
            'charset': 'utf8mb4',
        } if os.getenv('DATABASE_ENGINE', '').find('mysql') != -1 else {},
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend', # Domyślny backend
    'allauth.account.auth_backends.AuthenticationBackend', # Backend allauth
]
SITE_ID = 1 # Potrzebne dla django-allauth

LOGIN_REDIRECT_URL = '/'  # Gdzie przekierować po zalogowaniu
LOGOUT_REDIRECT_URL = '/' # Gdzie przekierować po wylogowaniu

# Django-allauth settings (updated to new format)
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # 5 attempts per 5 minutes
}
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH = 8

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',  # Lub 'offline', jeśli potrzebujesz odświeżania tokenu
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pl-pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "faktury", "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Ustawienia media files (pliki przesyłane przez użytkowników, np. logo firmy)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'  # REMOVE THIS LINE

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1', 'yes', 'on')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() in ('true', '1', 'yes', 'on')
SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() in ('true', '1', 'yes', 'on')
SECURE_CONTENT_TYPE_NOSNIFF = os.getenv('SECURE_CONTENT_TYPE_NOSNIFF', 'True').lower() in ('true', '1', 'yes', 'on')
SECURE_BROWSER_XSS_FILTER = os.getenv('SECURE_BROWSER_XSS_FILTER', 'True').lower() in ('true', '1', 'yes', 'on')
X_FRAME_OPTIONS = os.getenv('X_FRAME_OPTIONS', 'DENY')

# CSRF & Session security
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes', 'on')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes', 'on')
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# Email configuration
if DEBUG:
    # For development - print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # For production - use SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'mail.ooxo.pl')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes', 'on')
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'xo@ooxo.pl')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@faktulove.pl')
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[FaktuLove] '

# ============================================================================
# OCR AND AI CONFIGURATION
# ============================================================================

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'faktulove-ocr')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Document AI Configuration
DOCUMENT_AI_CONFIG = {
    'project_id': GOOGLE_CLOUD_PROJECT,
    'location': 'eu',  # Europe for GDPR compliance
    'processor_id': os.getenv('DOCUMENT_AI_PROCESSOR_ID'),
    'processor_version': 'rc',  # Release candidate for latest features
    'timeout': 30,  # seconds
    'max_file_size': 10 * 1024 * 1024,  # 10MB limit
}

# Supported file types for OCR
SUPPORTED_DOCUMENT_TYPES = {
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/tiff': '.tiff',
    'image/gif': '.gif',
}

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

# Redis Cache Configuration for distributed rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'faktulove',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Cache key versioning
CACHE_MIDDLEWARE_KEY_PREFIX = 'faktulove'
CACHE_MIDDLEWARE_SECONDS = 300

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# Celery Configuration
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Custom JSON encoder for Decimal objects
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_STORE_EAGER_RESULT = True

# Custom JSON encoder
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_STORE_EAGER_RESULT = True
CELERY_TASK_SERIALIZER_KWARGS = {'cls': DecimalEncoder}
CELERY_RESULT_SERIALIZER_KWARGS = {'cls': DecimalEncoder}

# Task routing
CELERY_TASK_ROUTES = {
    'faktury.tasks.process_ocr_document': {'queue': 'ocr'},
    'faktury.tasks.cleanup_old_documents': {'queue': 'cleanup'},
}

# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'ocr_upload': '10/min',
        'ocr_api': '100/min',
        'ocr_anon': '5/min',
        'ocr_burst': '30/min',
        'ocr_status': '200/min',
    },
    'EXCEPTION_HANDLER': 'faktury.api.exceptions.custom_exception_handler',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# CORS Configuration for React Frontend
CORS_ALLOWED_ORIGINS = [
    "https://app.ooxo.pl",
    "https://faktulove.pl",
]

if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ============================================================================
# OCR PROCESSING CONFIGURATION
# ============================================================================

# OCR Processing Settings
OCR_SETTINGS = {
    'confidence_thresholds': {
        'auto_approve': 0.95,    # Above 95% - auto-process
        'review_required': 0.80, # 80-95% - human review
        'manual_entry': 0.80,    # Below 80% - manual entry
    },
    'max_processing_time': 300,  # 5 minutes timeout
    'retry_attempts': 3,
    'cleanup_after_days': 30,    # Delete processed files after 30 days
}

# Polish language patterns for OCR enhancement
POLISH_OCR_PATTERNS = {
    'vat_patterns': [
        r'VAT\s*(\d{1,2})%',
        r'PTU\s*(\d{1,2})%', 
        r'(\d{1,2})\s*%\s*VAT',
    ],
    'date_patterns': [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',   # DD-MM-YYYY
    ],
    'nip_pattern': r'NIP:?\s*(\d{3}[- ]?\d{3}[- ]?\d{2}[- ]?\d{2})',
    'currency_patterns': [
        r'(\d+[,.]?\d*)\s*PLN',
        r'PLN\s*(\d+[,.]?\d*)',
        r'(\d+[,.]?\d*)\s*zł',
    ],
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create logs directory if it doesn't exist
import os
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Import API logging configuration
from faktury.api.logging_config import API_LOGGING_CONFIG

# Merge with existing logging configuration
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
        'api_json': {
            '()': 'faktury.api.logging_config.APILoggingFormatter',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django_errors.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'api.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'api_json',
        },
        'api_error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'api_errors.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'api_json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'security.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'api_json',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'faktury': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api': {
            'handlers': ['api_file', 'api_error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.requests': {
            'handlers': ['api_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.operations': {
            'handlers': ['api_file', 'api_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'faktury.api.security': {
            'handlers': ['security_file', 'api_error_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'faktury.api.views': {
            'handlers': ['api_file', 'api_error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# In production, reduce console logging
if not DEBUG:
    LOGGING['handlers']['console']['level'] = 'WARNING'
    for logger_config in LOGGING['loggers'].values():
        if 'console' in logger_config.get('handlers', []):
            # Keep console for errors only in production
            pass

# ============================================================================
# API DOCUMENTATION CONFIGURATION
# ============================================================================

# drf-spectacular settings for OpenAPI schema generation
SPECTACULAR_SETTINGS = {
    'TITLE': 'FaktuLove OCR API',
    'DESCRIPTION': '''
    Comprehensive RESTful API for OCR document processing in the FaktuLove invoice management system.
    
    This API provides secure endpoints for:
    - Document upload and OCR processing
    - Real-time processing status tracking
    - OCR results retrieval with filtering and pagination
    - Manual validation and correction of extracted data
    - Automatic invoice generation from validated OCR results
    
    ## Authentication
    
    The API supports multiple authentication methods:
    - **JWT Token Authentication** (recommended for frontend applications)
    - **Session Authentication** (for web browser access)
    - **Token Authentication** (for simple API access)
    
    ## Rate Limiting
    
    API endpoints are rate-limited to ensure fair usage:
    - File uploads: 10 requests per minute per user
    - General API calls: 100 requests per minute per user
    - Status checks: 200 requests per minute per user
    
    ## File Upload Requirements
    
    - **Supported formats**: PDF, JPEG, PNG
    - **Maximum file size**: 10MB
    - **Security**: All files are scanned for malware and validated
    
    ## Response Format
    
    All API responses follow a consistent JSON structure:
    ```json
    {
        "success": true,
        "data": { ... },
        "message": "Operation completed successfully",
        "timestamp": "2025-08-23T10:30:00Z"
    }
    ```
    
    Error responses include detailed error information:
    ```json
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid file format",
            "details": { ... }
        },
        "timestamp": "2025-08-23T10:30:00Z"
    }
    ```
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'CONTACT': {
        'name': 'FaktuLove API Support',
        'email': 'api-support@faktulove.pl',
        'url': 'https://faktulove.pl/support',
    },
    'LICENSE': {
        'name': 'Proprietary',
        'url': 'https://faktulove.pl/license',
    },
    'EXTERNAL_DOCS': {
        'description': 'FaktuLove Documentation',
        'url': 'https://docs.faktulove.pl',
    },
    
    # Schema generation settings
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'ENUM_NAME_OVERRIDES': {
        'ProcessingStatusEnum': 'faktury.models.OCRResult.PROCESSING_STATUS_CHOICES',
        'ConfidenceLevelEnum': 'faktury.models.OCRResult.CONFIDENCE_LEVEL_CHOICES',
    },
    
    # Authentication configuration
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    
    # API versioning
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
    'SCHEMA_PATH_PREFIX_TRIM': True,
    
    # Documentation customization
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'defaultModelsExpandDepth': 2,
        'defaultModelExpandDepth': 2,
        'displayRequestDuration': True,
        'docExpansion': 'list',
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
    },
    
    # Redoc settings
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'hideHostname': False,
        'hideLoading': False,
        'hideSchemaPattern': True,
        'expandResponses': '200,201',
        'pathInMiddlePanel': True,
        'nativeScrollbars': False,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#1976d2'
                }
            },
            'typography': {
                'fontSize': '14px',
                'lineHeight': '1.5em',
                'code': {
                    'fontSize': '13px'
                }
            }
        }
    },
    
    # Schema customization
    # 'PREPROCESSING_HOOKS': [
    #     'faktury.api.schema_hooks.preprocess_schema_result_hook',
    # ],
    # 'POSTPROCESSING_HOOKS': [
    #     'faktury.api.schema_hooks.postprocess_schema_hook',
    # ],
    
    # Error handling
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': [],
    
    # Tags for grouping endpoints
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'User authentication and token management endpoints'
        },
        {
            'name': 'OCR Upload',
            'description': 'Document upload endpoints for OCR processing'
        },
        {
            'name': 'OCR Status',
            'description': 'Processing status tracking endpoints'
        },
        {
            'name': 'OCR Results',
            'description': 'OCR results retrieval and management endpoints'
        },
        {
            'name': 'OCR Validation',
            'description': 'Manual validation and correction endpoints'
        },
    ],
}

# ============================================================================
# ERROR HANDLING CONFIGURATION
# ============================================================================

# Custom error handling settings
API_ERROR_HANDLING = {
    'log_sensitive_data': DEBUG,  # Only log sensitive data in development
    'include_stack_trace': DEBUG,  # Only include stack traces in development
    'max_error_details_length': 1000,  # Limit error details length
    'rate_limit_retry_after': 60,  # Default retry after seconds for rate limiting
    'security_log_failed_attempts': True,  # Log failed authentication attempts
}

# Error monitoring settings (for production)
ERROR_MONITORING = {
    'enabled': not DEBUG,
    'sample_rate': 0.1,  # Sample 10% of errors for performance
    'ignore_errors': [
        'django.http.Http404',
        'django.core.exceptions.PermissionDenied',
    ],
}