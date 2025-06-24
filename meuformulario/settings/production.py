import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Allow Railway domain
ALLOWED_HOSTS = [
    '.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# Database
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

# Static files configuration for production
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Update Wagtail admin base URL for production
WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL', 'https://your-app.railway.app')

try:
    from .local import *
except ImportError:
    pass
