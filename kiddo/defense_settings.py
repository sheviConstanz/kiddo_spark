"""Opt-in academic fixture in its own SQLite file and browser session."""
import json
import os
import re

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403

DEFENSE_DIRECTORY = BASE_DIR / 'var' / 'defense_data'
selected = os.environ.get('KIDDO_DEFENSE_DB')
if selected is None:
    pointer = DEFENSE_DIRECTORY / 'current.json'
    selected = json.loads(pointer.read_text(encoding='utf-8'))['database'] if pointer.exists() else 'defensa.sqlite3'
if not isinstance(selected, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+\.sqlite3', selected):
    raise ImproperlyConfigured('La base de defensa debe ser un nombre SQLite dentro de var/defense_data.')
DATABASES = {'default': {**DATABASES['default'], 'NAME': DEFENSE_DIRECTORY / selected}}
KIDDO_SEED_DEMO_ACCOUNTS = False
KIDDO_ALLOW_DEMO_DATA = True
KIDDO_DEFENSE_DEMO = True
MEDIA_ROOT = DEFENSE_DIRECTORY / 'uploads'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']
SESSION_COOKIE_NAME = 'kiddo_defense_session'
CSRF_COOKIE_NAME = 'kiddo_defense_csrf'
