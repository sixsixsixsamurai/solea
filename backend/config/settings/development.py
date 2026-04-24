from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Remove WhiteNoise in dev — Django's runserver serves static files directly
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]

# Serve static files directly from STATICFILES_DIRS (no hashing, no collectstatic needed)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Show emails in console during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (optional, install separately)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
