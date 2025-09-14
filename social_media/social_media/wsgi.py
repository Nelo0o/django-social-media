"""
WSGI config for social_media project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Configuration pour Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings_vercel')

application = get_wsgi_application()

# Vercel handler
app = application
