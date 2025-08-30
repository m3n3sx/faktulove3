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

ALLOWED_HOSTS = ['*']
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
    'faktury.middleware.ocr_security_middleware.OCRSecurityMiddleware',  # OCR security middleware - moved after auth
    'faktury.middleware.ocr_security_middleware.OCRFileSecurityMiddleware',  # OCR file security middleware - moved after auth
    'faktury.api.responses.APIResponseMiddleware',  # Add API response middleware
    'faktury.api.logging_config.APIRequestLoggingMiddleware',  # Add API logging middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'faktury.middleware.FirmaCheckMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # Compression middleware
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
                'faktury.context_processors.global_context',
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

# Static file caching and optimization
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Cache settings for static files
STATICFILES_CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 30 days
STATICFILES_CACHE_HEADERS = {
    'Cache-Control': 'public, max-age=2592000',  # 30 days
    'Expires': 'Thu, 31 Dec 2025 23:59:59 GMT',
}

# Compression settings
COMPRESS_ENABLED = os.getenv('COMPRESS_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on')
COMPRESS_OFFLINE = os.getenv('COMPRESS_OFFLINE', 'False').lower() in ('true', '1', 'yes', 'on')
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

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

# Feature flags for OCR system
OCR_FEATURE_FLAGS = {
    # Core OCR flags
    'use_paddleocr': os.getenv('USE_PADDLEOCR', 'True').lower() in ('true', '1', 'yes', 'on'),
    'paddleocr_primary': os.getenv('PADDLEOCR_PRIMARY', 'True').lower() in ('true', '1', 'yes', 'on'),
    'use_opensource_ocr': os.getenv('USE_OPENSOURCE_OCR', 'True').lower() in ('true', '1', 'yes', 'on'),
    'disable_google_cloud': os.getenv('DISABLE_GOOGLE_CLOUD', 'True').lower() in ('true', '1', 'yes', 'on'),
    'validate_ocr_config': os.getenv('VALIDATE_OCR_CONFIG', 'True').lower() in ('true', '1', 'yes', 'on'),
    
    # Security flags
    'enable_security_features': os.getenv('ENABLE_OCR_SECURITY', 'True').lower() in ('true', '1', 'yes', 'on'),
    'require_encryption': os.getenv('REQUIRE_OCR_ENCRYPTION', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_audit_logging': os.getenv('ENABLE_OCR_AUDIT_LOGGING', 'True').lower() in ('true', '1', 'yes', 'on'),
    
    # PaddleOCR specific flags
    'enable_gpu_acceleration': os.getenv('PADDLEOCR_ENABLE_GPU', 'False').lower() in ('true', '1', 'yes', 'on'),
    'advanced_preprocessing': os.getenv('PADDLEOCR_ADVANCED_PREPROCESSING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'polish_pattern_enhancement': os.getenv('PADDLEOCR_POLISH_ENHANCEMENT', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_confidence_boosting': os.getenv('PADDLEOCR_CONFIDENCE_BOOSTING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_spatial_analysis': os.getenv('PADDLEOCR_SPATIAL_ANALYSIS', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_fallback_handling': os.getenv('PADDLEOCR_FALLBACK_HANDLING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_performance_monitoring': os.getenv('PADDLEOCR_PERFORMANCE_MONITORING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_memory_optimization': os.getenv('PADDLEOCR_MEMORY_OPTIMIZATION', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_model_caching': os.getenv('PADDLEOCR_MODEL_CACHING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'enable_batch_processing': os.getenv('PADDLEOCR_BATCH_PROCESSING', 'False').lower() in ('true', '1', 'yes', 'on'),
    'enable_debug_mode': os.getenv('PADDLEOCR_DEBUG_MODE', 'False').lower() in ('true', '1', 'yes', 'on'),
}

# Open Source OCR Configuration
OCR_CONFIG = {
    # Service configuration
    'service_url': os.getenv('OCR_SERVICE_URL', 'http://localhost:8001'),
    'timeout': int(os.getenv('OCR_TIMEOUT', '30')),
    'max_retries': int(os.getenv('OCR_MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('OCR_RETRY_DELAY', '5')),
    
    # File processing limits
    'max_file_size': 10 * 1024 * 1024,  # 10MB limit
    'supported_formats': ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'],
    
    # OCR engines configuration
    'engines': {
        'tesseract': {
            'enabled': True,
            'language': 'pol+eng',
            'timeout': 30,
            'config': '--psm 6 --oem 3'  # Page segmentation and OCR engine mode
        },
        'easyocr': {
            'enabled': True,
            'languages': ['pl', 'en'],
            'gpu': False,
            'confidence_threshold': 0.5
        }
    },
    
    # Image preprocessing settings
    'preprocessing': {
        'enabled': True,
        'deskew': True,
        'denoise': True,
        'enhance_contrast': True,
        'binarize': True
    },
    
    # Polish language specific settings
    'polish_patterns': {
        'nip_pattern': r'\b\d{3}-?\d{3}-?\d{2}-?\d{2}\b',
        'date_patterns': [
            r'\b(\d{1,2})[.-](\d{1,2})[.-](\d{4})\b',
            r'\b(\d{4})[.-](\d{1,2})[.-](\d{1,2})\b'
        ],
        'amount_patterns': [
            r'\b\d{1,3}(?:\s?\d{3})*[,.]?\d{0,2}\s?(?:zł|PLN|pln)\b',
            r'\b\d+[,.]\d{2}\b'
        ],
        'invoice_number_patterns': [
            r'(?:FV|faktura|invoice)[:\s]*([A-Z0-9\/\-]+)',
            r'(?:Nr|No|Number)[:\s]*([A-Z0-9\/\-]+)'
        ]
    },
    
    # Confidence scoring
    'confidence': {
        'min_threshold': 0.5,
        'high_threshold': 0.8,
        'polish_boost': 0.1,  # Boost confidence for recognized Polish patterns
        'validation_boost': 0.15  # Boost for validated data (NIP, dates, etc.)
    },
    
    # Security configuration
    'security': {
        'encrypt_temp_files': True,
        'secure_file_deletion': True,
        'audit_all_operations': True,
        'require_authentication': True,
        'validate_on_premises': True,
        'cleanup_after_processing': True,
        'max_file_age_hours': 24,
        'allowed_file_types': ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'],
        'max_file_size_mb': 10,
        'rate_limits': {
            'upload': {'requests': 10, 'window_minutes': 5},
            'process': {'requests': 20, 'window_minutes': 5},
            'validate': {'requests': 50, 'window_minutes': 5}
        }
    }
}

# Supported file types for OCR
SUPPORTED_DOCUMENT_TYPES = {
    'application/pdf': '.pdf',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/tiff': '.tiff',
    'image/gif': '.gif',
}

# OCR Engine Priority Configuration
OCR_ENGINE_PRIORITY = [
    'paddleocr',    # Primary engine - best for Polish documents
    'tesseract',    # Secondary fallback
    'easyocr',      # Tertiary fallback
    'google'        # Final fallback (if enabled)
]

# PaddleOCR Configuration
PADDLEOCR_CONFIG = {
    # Core configuration
    'enabled': os.getenv('PADDLEOCR_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
    'languages': os.getenv('PADDLEOCR_LANGUAGES', 'pl,en').split(','),
    'use_gpu': os.getenv('PADDLEOCR_USE_GPU', 'False').lower() in ('true', '1', 'yes', 'on'),
    'model_dir': os.getenv('PADDLEOCR_MODEL_DIR', os.path.join(BASE_DIR, 'paddle_models')),
    'det_model_name': os.getenv('PADDLEOCR_DET_MODEL', 'pl_PP-OCRv4_det'),
    'rec_model_name': os.getenv('PADDLEOCR_REC_MODEL', 'pl_PP-OCRv4_rec'),
    'cls_model_name': os.getenv('PADDLEOCR_CLS_MODEL', 'ch_ppocr_mobile_v2.0_cls'),
    'max_text_length': int(os.getenv('PADDLEOCR_MAX_TEXT_LENGTH', '25000')),
    'use_angle_cls': os.getenv('PADDLEOCR_USE_ANGLE_CLS', 'True').lower() in ('true', '1', 'yes', 'on'),
    'use_space_char': os.getenv('PADDLEOCR_USE_SPACE_CHAR', 'True').lower() in ('true', '1', 'yes', 'on'),
    'drop_score': float(os.getenv('PADDLEOCR_DROP_SCORE', '0.5')),
    'timeout': int(os.getenv('PADDLEOCR_TIMEOUT', '30')),
    'max_retries': int(os.getenv('PADDLEOCR_MAX_RETRIES', '2')),
    'max_file_size': int(os.getenv('PADDLEOCR_MAX_FILE_SIZE', str(50 * 1024 * 1024))),  # 50MB default
    
    # Performance configuration
    'max_memory_mb': int(os.getenv('PADDLEOCR_MAX_MEMORY', '800')),
    'max_workers': int(os.getenv('PADDLEOCR_MAX_WORKERS', '2')),
    'batch_size': int(os.getenv('PADDLEOCR_BATCH_SIZE', '1')),
    'enable_parallel_processing': os.getenv('PADDLEOCR_PARALLEL_PROCESSING', 'False').lower() in ('true', '1', 'yes', 'on'),
    'cpu_threads': int(os.getenv('PADDLEOCR_CPU_THREADS', '4')),
    'enable_mkldnn': os.getenv('PADDLEOCR_ENABLE_MKLDNN', 'True').lower() in ('true', '1', 'yes', 'on'),
    
    # Preprocessing configuration
    'preprocessing': {
        'enabled': os.getenv('PADDLEOCR_PREPROCESSING_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
        'noise_reduction': os.getenv('PADDLEOCR_NOISE_REDUCTION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'contrast_enhancement': os.getenv('PADDLEOCR_CONTRAST_ENHANCEMENT', 'True').lower() in ('true', '1', 'yes', 'on'),
        'skew_correction': os.getenv('PADDLEOCR_SKEW_CORRECTION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'resolution_optimization': os.getenv('PADDLEOCR_RESOLUTION_OPTIMIZATION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'adaptive_threshold': os.getenv('PADDLEOCR_ADAPTIVE_THRESHOLD', 'True').lower() in ('true', '1', 'yes', 'on'),
        'morphological_operations': os.getenv('PADDLEOCR_MORPHOLOGICAL_OPS', 'True').lower() in ('true', '1', 'yes', 'on'),
    },
    
    # Polish optimization configuration
    'polish_optimization': {
        'enabled': os.getenv('PADDLEOCR_POLISH_OPTIMIZATION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'nip_validation': os.getenv('PADDLEOCR_NIP_VALIDATION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'date_format_enhancement': os.getenv('PADDLEOCR_DATE_ENHANCEMENT', 'True').lower() in ('true', '1', 'yes', 'on'),
        'currency_parsing': os.getenv('PADDLEOCR_CURRENCY_PARSING', 'True').lower() in ('true', '1', 'yes', 'on'),
        'spatial_analysis': os.getenv('PADDLEOCR_SPATIAL_ANALYSIS', 'True').lower() in ('true', '1', 'yes', 'on'),
        'confidence_boosting': os.getenv('PADDLEOCR_CONFIDENCE_BOOSTING', 'True').lower() in ('true', '1', 'yes', 'on'),
        'pattern_validation': os.getenv('PADDLEOCR_PATTERN_VALIDATION', 'True').lower() in ('true', '1', 'yes', 'on'),
    },
    
    # Error handling configuration
    'fallback': {
        'enabled': os.getenv('PADDLEOCR_FALLBACK_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
        'strategy': os.getenv('PADDLEOCR_FALLBACK_STRATEGY', 'retry_then_fallback'),
        'max_retries': int(os.getenv('PADDLEOCR_FALLBACK_MAX_RETRIES', '2')),
        'retry_delay': float(os.getenv('PADDLEOCR_FALLBACK_RETRY_DELAY', '1.0')),
        'fallback_engines': os.getenv('PADDLEOCR_FALLBACK_ENGINES', 'tesseract,easyocr').split(','),
        'auto_fallback_threshold': float(os.getenv('PADDLEOCR_AUTO_FALLBACK_THRESHOLD', '0.3')),
    },
    
    # Memory monitoring configuration
    'memory': {
        'max_memory_mb': float(os.getenv('PADDLEOCR_MEMORY_MAX', '800.0')),
        'warning_threshold_mb': float(os.getenv('PADDLEOCR_MEMORY_WARNING', '600.0')),
        'critical_threshold_mb': float(os.getenv('PADDLEOCR_MEMORY_CRITICAL', '750.0')),
        'optimization_level': os.getenv('PADDLEOCR_MEMORY_OPTIMIZATION', 'basic'),
        'enable_alerts': os.getenv('PADDLEOCR_MEMORY_ALERTS', 'True').lower() in ('true', '1', 'yes', 'on'),
        'cleanup_interval': int(os.getenv('PADDLEOCR_MEMORY_CLEANUP_INTERVAL', '300')),  # 5 minutes
        'force_gc': os.getenv('PADDLEOCR_FORCE_GC', 'True').lower() in ('true', '1', 'yes', 'on'),
    },
    
    # Timeout configuration
    'timeouts': {
        'initialization': float(os.getenv('PADDLEOCR_TIMEOUT_INIT', '60.0')),
        'processing': float(os.getenv('PADDLEOCR_TIMEOUT_PROCESSING', '30.0')),
        'model_loading': float(os.getenv('PADDLEOCR_TIMEOUT_MODEL_LOADING', '120.0')),
        'preprocessing': float(os.getenv('PADDLEOCR_TIMEOUT_PREPROCESSING', '15.0')),
        'postprocessing': float(os.getenv('PADDLEOCR_TIMEOUT_POSTPROCESSING', '10.0')),
        'strategy': os.getenv('PADDLEOCR_TIMEOUT_STRATEGY', 'graceful'),
        'enable_degradation': os.getenv('PADDLEOCR_TIMEOUT_DEGRADATION', 'True').lower() in ('true', '1', 'yes', 'on'),
    },
    
    # Confidence scoring configuration
    'confidence': {
        'min_threshold': float(os.getenv('PADDLEOCR_CONFIDENCE_MIN', '0.5')),
        'high_threshold': float(os.getenv('PADDLEOCR_CONFIDENCE_HIGH', '0.8')),
        'polish_boost': float(os.getenv('PADDLEOCR_CONFIDENCE_POLISH_BOOST', '0.1')),
        'validation_boost': float(os.getenv('PADDLEOCR_CONFIDENCE_VALIDATION_BOOST', '0.15')),
        'spatial_consistency_weight': float(os.getenv('PADDLEOCR_CONFIDENCE_SPATIAL_WEIGHT', '0.2')),
        'pattern_match_weight': float(os.getenv('PADDLEOCR_CONFIDENCE_PATTERN_WEIGHT', '0.3')),
    },
    
    # Logging and monitoring configuration
    'logging': {
        'enabled': os.getenv('PADDLEOCR_LOGGING_ENABLED', 'True').lower() in ('true', '1', 'yes', 'on'),
        'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
        'performance_logging': os.getenv('PADDLEOCR_PERFORMANCE_LOGGING', 'True').lower() in ('true', '1', 'yes', 'on'),
        'error_logging': os.getenv('PADDLEOCR_ERROR_LOGGING', 'True').lower() in ('true', '1', 'yes', 'on'),
        'debug_mode': os.getenv('PADDLEOCR_DEBUG_MODE', 'False').lower() in ('true', '1', 'yes', 'on'),
    },
    
    # Model management configuration
    'models': {
        'auto_download': os.getenv('PADDLEOCR_AUTO_DOWNLOAD_MODELS', 'True').lower() in ('true', '1', 'yes', 'on'),
        'model_cache_size': int(os.getenv('PADDLEOCR_MODEL_CACHE_SIZE', '3')),
        'model_validation': os.getenv('PADDLEOCR_MODEL_VALIDATION', 'True').lower() in ('true', '1', 'yes', 'on'),
        'update_check_interval': int(os.getenv('PADDLEOCR_MODEL_UPDATE_CHECK', '86400')),  # 24 hours
        'backup_models': os.getenv('PADDLEOCR_BACKUP_MODELS', 'True').lower() in ('true', '1', 'yes', 'on'),
    }
}

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# ============================================================================
# PADDLEOCR PERFORMANCE TUNING
# ============================================================================

# Performance optimization settings for PaddleOCR
PADDLEOCR_PERFORMANCE_CONFIG = {
    # Resource allocation
    'max_concurrent_requests': int(os.getenv('PADDLEOCR_MAX_CONCURRENT_REQUESTS', '3')),
    'request_queue_size': int(os.getenv('PADDLEOCR_REQUEST_QUEUE_SIZE', '10')),
    'worker_pool_size': int(os.getenv('PADDLEOCR_WORKER_POOL_SIZE', '2')),
    
    # Memory optimization
    'memory_pool_size': int(os.getenv('PADDLEOCR_MEMORY_POOL_SIZE', '512')),  # MB
    'enable_memory_mapping': os.getenv('PADDLEOCR_MEMORY_MAPPING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'garbage_collection_threshold': int(os.getenv('PADDLEOCR_GC_THRESHOLD', '100')),
    'memory_cleanup_interval': int(os.getenv('PADDLEOCR_MEMORY_CLEANUP_INTERVAL', '300')),  # seconds
    
    # Processing optimization
    'enable_batch_processing': os.getenv('PADDLEOCR_ENABLE_BATCH_PROCESSING', 'False').lower() in ('true', '1', 'yes', 'on'),
    'batch_timeout': int(os.getenv('PADDLEOCR_BATCH_TIMEOUT', '5')),  # seconds
    'max_batch_size': int(os.getenv('PADDLEOCR_MAX_BATCH_SIZE', '5')),
    'enable_async_processing': os.getenv('PADDLEOCR_ASYNC_PROCESSING', 'True').lower() in ('true', '1', 'yes', 'on'),
    
    # Model optimization
    'model_warmup_enabled': os.getenv('PADDLEOCR_MODEL_WARMUP', 'True').lower() in ('true', '1', 'yes', 'on'),
    'model_preload_enabled': os.getenv('PADDLEOCR_MODEL_PRELOAD', 'True').lower() in ('true', '1', 'yes', 'on'),
    'model_cache_ttl': int(os.getenv('PADDLEOCR_MODEL_CACHE_TTL', '3600')),  # seconds
    'enable_model_quantization': os.getenv('PADDLEOCR_MODEL_QUANTIZATION', 'False').lower() in ('true', '1', 'yes', 'on'),
    
    # Image processing optimization
    'max_image_dimension': int(os.getenv('PADDLEOCR_MAX_IMAGE_DIMENSION', '2048')),
    'image_compression_quality': int(os.getenv('PADDLEOCR_IMAGE_COMPRESSION_QUALITY', '85')),
    'enable_image_caching': os.getenv('PADDLEOCR_IMAGE_CACHING', 'True').lower() in ('true', '1', 'yes', 'on'),
    'image_cache_size': int(os.getenv('PADDLEOCR_IMAGE_CACHE_SIZE', '100')),  # number of images
    
    # CPU optimization
    'cpu_optimization_level': os.getenv('PADDLEOCR_CPU_OPTIMIZATION', 'medium'),  # low, medium, high
    'enable_cpu_affinity': os.getenv('PADDLEOCR_CPU_AFFINITY', 'False').lower() in ('true', '1', 'yes', 'on'),
    'cpu_core_allocation': os.getenv('PADDLEOCR_CPU_CORES', 'auto'),  # auto, or specific cores like "0,1,2,3"
    
    # I/O optimization
    'enable_io_optimization': os.getenv('PADDLEOCR_IO_OPTIMIZATION', 'True').lower() in ('true', '1', 'yes', 'on'),
    'io_buffer_size': int(os.getenv('PADDLEOCR_IO_BUFFER_SIZE', '8192')),  # bytes
    'enable_async_io': os.getenv('PADDLEOCR_ASYNC_IO', 'True').lower() in ('true', '1', 'yes', 'on'),
    
    # Monitoring and profiling
    'enable_performance_profiling': os.getenv('PADDLEOCR_PERFORMANCE_PROFILING', 'False').lower() in ('true', '1', 'yes', 'on'),
    'profiling_sample_rate': float(os.getenv('PADDLEOCR_PROFILING_SAMPLE_RATE', '0.1')),  # 10% of requests
    'enable_metrics_collection': os.getenv('PADDLEOCR_METRICS_COLLECTION', 'True').lower() in ('true', '1', 'yes', 'on'),
    'metrics_retention_days': int(os.getenv('PADDLEOCR_METRICS_RETENTION', '7')),
}

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
    # PaddleOCR specific task routing
    'faktury.tasks.process_paddleocr_document': {'queue': 'paddleocr'},
    'faktury.tasks.paddleocr_batch_process': {'queue': 'paddleocr_batch'},
    'faktury.tasks.paddleocr_model_warmup': {'queue': 'paddleocr_maintenance'},
    'faktury.tasks.paddleocr_performance_monitoring': {'queue': 'monitoring'},
    'faktury.tasks.paddleocr_memory_cleanup': {'queue': 'cleanup'},
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
        'ocr_upload': '50/min',  # Increased from 10/min for development
        'ocr_api': '100/min',
        'ocr_anon': '5/min',
        'ocr_burst': '30/min',
        'ocr_status': '200/min',
        # PaddleOCR specific throttling
        'paddleocr_upload': os.getenv('PADDLEOCR_THROTTLE_UPLOAD', '8/min'),
        'paddleocr_process': os.getenv('PADDLEOCR_THROTTLE_PROCESS', '15/min'),
        'paddleocr_batch': os.getenv('PADDLEOCR_THROTTLE_BATCH', '3/min'),
        'paddleocr_heavy': os.getenv('PADDLEOCR_THROTTLE_HEAVY', '5/min'),  # For large files
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
        # PaddleOCR specific logging
        'faktury.services.paddle_ocr_service': {
            'handlers': ['console', 'file', 'error_file'],
            'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
            'propagate': False,
        },
        'faktury.services.paddle_ocr_engine': {
            'handlers': ['console', 'file', 'error_file'],
            'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
            'propagate': False,
        },
        'faktury.services.enhanced_polish_processor': {
            'handlers': ['console', 'file'],
            'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
            'propagate': False,
        },
        'faktury.services.paddle_confidence_calculator': {
            'handlers': ['console', 'file'],
            'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
            'propagate': False,
        },
        'faktury.services.advanced_image_preprocessor': {
            'handlers': ['console', 'file'],
            'level': os.getenv('PADDLEOCR_LOGGING_LEVEL', 'INFO'),
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
# PADDLEOCR CONFIGURATION VALIDATION
# ============================================================================

def validate_paddleocr_config():
    """Validate PaddleOCR configuration settings"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Only validate if PaddleOCR is enabled
    if not PADDLEOCR_CONFIG.get('enabled', False):
        return True
    
    validation_errors = []
    
    # Validate model directory
    model_dir = PADDLEOCR_CONFIG.get('model_dir')
    if not model_dir:
        validation_errors.append("PADDLEOCR_MODEL_DIR is required when PaddleOCR is enabled")
    
    # Validate memory settings
    max_memory = PADDLEOCR_CONFIG.get('max_memory_mb', 0)
    if max_memory <= 0:
        validation_errors.append("PADDLEOCR_MAX_MEMORY must be greater than 0")
    
    warning_threshold = PADDLEOCR_CONFIG['memory']['warning_threshold_mb']
    critical_threshold = PADDLEOCR_CONFIG['memory']['critical_threshold_mb']
    
    if warning_threshold >= critical_threshold:
        validation_errors.append("PADDLEOCR memory warning threshold must be less than critical threshold")
    
    if critical_threshold >= max_memory:
        validation_errors.append("PADDLEOCR memory critical threshold must be less than max memory")
    
    # Validate timeout settings
    timeouts = PADDLEOCR_CONFIG.get('timeouts', {})
    processing_timeout = timeouts.get('processing', 0)
    if processing_timeout <= 0:
        validation_errors.append("PADDLEOCR processing timeout must be greater than 0")
    
    # Validate confidence thresholds
    confidence = PADDLEOCR_CONFIG.get('confidence', {})
    min_threshold = confidence.get('min_threshold', 0)
    high_threshold = confidence.get('high_threshold', 0)
    
    if not (0 <= min_threshold <= 1):
        validation_errors.append("PADDLEOCR confidence min_threshold must be between 0 and 1")
    
    if not (0 <= high_threshold <= 1):
        validation_errors.append("PADDLEOCR confidence high_threshold must be between 0 and 1")
    
    if min_threshold >= high_threshold:
        validation_errors.append("PADDLEOCR confidence min_threshold must be less than high_threshold")
    
    # Validate worker settings
    max_workers = PADDLEOCR_CONFIG.get('max_workers', 0)
    if max_workers <= 0:
        validation_errors.append("PADDLEOCR_MAX_WORKERS must be greater than 0")
    
    # Validate performance settings
    perf_config = PADDLEOCR_PERFORMANCE_CONFIG
    max_concurrent = perf_config.get('max_concurrent_requests', 0)
    if max_concurrent <= 0:
        validation_errors.append("PADDLEOCR_MAX_CONCURRENT_REQUESTS must be greater than 0")
    
    # Log validation results
    if validation_errors:
        logger.error("PaddleOCR configuration validation failed:")
        for error in validation_errors:
            logger.error(f"  - {error}")
        
        if OCR_FEATURE_FLAGS.get('validate_ocr_config', True):
            raise ValueError(f"PaddleOCR configuration validation failed: {'; '.join(validation_errors)}")
    else:
        logger.info("PaddleOCR configuration validation passed")
    
    return len(validation_errors) == 0

# Run validation if enabled
if OCR_FEATURE_FLAGS.get('validate_ocr_config', True) and PADDLEOCR_CONFIG.get('enabled', False):
    try:
        validate_paddleocr_config()
    except Exception as e:
        # In development, log the error but don't crash
        if DEBUG:
            import logging
            logging.getLogger(__name__).warning(f"PaddleOCR configuration validation warning: {e}")
        else:
            # In production, this should be a hard failure
            raise

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

# ============================================================================
# STARTUP CONFIGURATION VALIDATION
# ============================================================================

# Validate OCR configuration on startup
def _validate_startup_configuration():
    """Validate critical configuration settings on startup"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Check OCR feature flags
    flags = OCR_FEATURE_FLAGS
    
    if flags.get('disable_google_cloud') and flags.get('validate_ocr_config'):
        # Ensure Google Cloud settings are not present when disabled
        deprecated_settings = ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_APPLICATION_CREDENTIALS', 'DOCUMENT_AI_CONFIG']
        for setting_name in deprecated_settings:
            if setting_name in globals() and globals()[setting_name]:
                logger.warning(f"Google Cloud setting '{setting_name}' is present but Google Cloud is disabled")
        
        # Ensure OCR_CONFIG is properly configured
        if not OCR_CONFIG:
            logger.error("OCR_CONFIG is required when using open source OCR")
        elif not OCR_CONFIG.get('engines'):
            logger.error("No OCR engines configured in OCR_CONFIG")
        
        logger.info("✅ OCR configuration validation completed")

# Run startup validation
try:
    _validate_startup_configuration()
except Exception as e:
    # Don't fail startup due to validation errors
    import logging
    logging.getLogger(__name__).warning(f"Startup configuration validation failed: {e}")