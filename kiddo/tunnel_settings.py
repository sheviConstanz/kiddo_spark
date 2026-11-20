"""Settings for the isolated, temporary presentation served by Dev Tunnels."""
import os
import re

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

from .settings import *  # noqa: F403

origin = os.environ.get('KIDDO_TUNNEL_ORIGIN', '')
if not re.fullmatch(r'https://[a-z0-9-]+-8001(?:\.[a-z0-9-]+)?\.devtunnels\.ms', origin):
    raise ImproperlyConfigured('Se requiere la URL HTTPS exacta de Dev Tunnels para el puerto 8001.')

DEBUG = False
KIDDO_SEED_DEMO_ACCOUNTS = False
SECRET_KEY = get_random_secret_key()
ALLOWED_HOSTS = [origin.removeprefix('https://'), '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [origin]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
DATABASES = {'default': {**DATABASES['default'], 'NAME': BASE_DIR / 'var' / 'kiddo_tunnel.sqlite3'}}
