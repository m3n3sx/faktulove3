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
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'app.ooxo.pl,167.114.96.110,faktulove.pl').split(',')
CSRF_TRUSTED_ORIGINS = [
    'https://app.ooxo.pl',
    'https://faktulove.pl',
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    #'faktury.middleware.FirmaCheckMiddleware',
]

ROOT_URLCONF = 'faktury_projekt.urls'

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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'faktury',
        'USER': 'faktury',
        'PASSWORD': 'CAnabis123#$',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
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
    #'allauth.account.auth_backends.AuthenticationBackend', # Backend allauth
]
SITE_ID = 1 # Potrzebne dla django-allauth

LOGIN_REDIRECT_URL = '/'  # Gdzie przekierować po zalogowaniu
LOGOUT_REDIRECT_URL = '/' # Gdzie przekierować po wylogowaniu
LOGIN_URL = '/accounts/login/'  # Gdzie przekierować gdy wymagane logowanie

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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.ooxo.pl'  # Adres serwera SMTP (np. smtp.gmail.com)
EMAIL_PORT = 587  # Port SMTP (zwykle 587 dla TLS, 465 dla SSL)
EMAIL_USE_TLS = True  # Używaj TLS (zalecane)
EMAIL_HOST_USER = 'xo@ooxo.pl'  # Twój adres e-mail
EMAIL_HOST_PASSWORD = 'CAnabis123#$'  # Hasło do Twojego e-maila (!!! UŻYWAJ HASŁA APLIKACJI !!!)
DEFAULT_FROM_EMAIL = 'xo@ooxo.pl' # Domyślny adres "Od"

# ============================================================================
# OCR AND AI CONFIGURATION
# ============================================================================

# Feature flags for OCR system
OCR_FEATURE_FLAGS = {
    'use_opensource_ocr': os.getenv('USE_OPENSOURCE_OCR', 'True').lower() in ('true', '1', 'yes', 'on'),
    'disable_google_cloud': os.getenv('DISABLE_GOOGLE_CLOUD', 'True').lower() in ('true', '1', 'yes', 'on'),
    'validate_ocr_config': os.getenv('VALIDATE_OCR_CONFIG', 'True').lower() in ('true', '1', 'yes', 'on'),
    'use_paddleocr': os.getenv('PADDLEOCR_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
    'paddleocr_primary': os.getenv('PADDLEOCR_PRIMARY', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_gpu_acceleration': os.getenv('PADDLEOCR_USE_GPU', 'False').lower() in ('true', '1', 'yes', 'on'),
    'advanced_preprocessing': True,
    'polish_pattern_enhancement': True,
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

# PaddleOCR Configuration
PADDLEOCR_CONFIG = {
    'enabled': os.getenv('PADDLEOCR_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
    'languages': os.getenv('PADDLEOCR_LANGUAGES', 'pl,en').split(','),
    'use_gpu': os.getenv('PADDLEOCR_USE_GPU', 'False').lower() in ('true', '1', 'yes', 'on'),
    'model_dir': os.getenv('PADDLEOCR_MODEL_DIR', os.path.join(BASE_DIR, 'paddle_models')),
    'det_model_name': 'pl_PP-OCRv4_det',
    'rec_model_name': 'pl_PP-OCRv4_rec', 
    'cls_model_name': 'ch_ppocr_mobile_v2.0_cls',
    'max_text_length': 25000,
    'use_angle_cls': True,
    'use_space_char': True,
    'drop_score': 0.5,
    'max_memory': int(os.getenv('PADDLEOCR_MAX_MEMORY', '800')),
    'max_workers': int(os.getenv('PADDLEOCR_MAX_WORKERS', '2')),
    'timeout': int(os.getenv('PADDLEOCR_TIMEOUT', '10')),
    'batch_size': int(os.getenv('PADDLEOCR_BATCH_SIZE', '1')),
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
    }
}

# OCR Engine Priority (PaddleOCR first if enabled)
OCR_ENGINE_PRIORITY = []
if PADDLEOCR_CONFIG['enabled']:
    OCR_ENGINE_PRIORITY.append('paddleocr')
OCR_ENGINE_PRIORITY.extend(['tesseract', 'easyocr'])
