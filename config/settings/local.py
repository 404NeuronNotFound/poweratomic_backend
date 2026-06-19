"""
Local development settings. Run with:
    DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver
(manage.py already defaults to this file, so you usually don't need to set it.)
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']  # fine for local dev; production.py locks this down

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Wide open for local dev so the Expo app can call the API from whatever
# LAN IP or simulator host it happens to be running on.
CORS_ALLOW_ALL_ORIGINS = True