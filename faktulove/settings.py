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
    'corsheaders',
    'django_celery_results',
    'django_celery_beat',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'faktury.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "https://app.ooxo.pl",
    "https://faktulove.pl",
]

if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
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
