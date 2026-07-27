"""Configuration pytest pour les tests Django Bloc4."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto_app.settings")
os.environ.setdefault("DJANGO_DB_ENGINE", "django.db.backends.sqlite3")
os.environ.setdefault("DJANGO_DB_NAME", ":memory:")

import django
django.setup()
