import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_deploy')

from django.conf import settings
from faktulove.settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE