"""
Production settings. Not wired up to a live server yet (that's a later
chunk - Docker + Railway/Render per the white paper) but the shape is here
so DEBUG and CORS can never accidentally stay wide open in production.
"""

import dj_database_url

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL')),
}

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True