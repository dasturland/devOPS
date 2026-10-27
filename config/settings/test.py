"""Fast settings for the automated test-suite (NFR-05)."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# Primary CI database is the PostgreSQL service (DATABASE_URL). Locally, with no
# DATABASE_URL set, we fall back to fast in-memory SQLite (NFR-11).
_database_url = env("DATABASE_URL")
if _database_url:
    from urllib.parse import urlparse

    _parsed = urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _parsed.path.lstrip("/"),
            "USER": _parsed.username or "",
            "PASSWORD": _parsed.password or "",
            "HOST": _parsed.hostname or "",
            "PORT": str(_parsed.port or ""),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Use the plain staticfiles backend so templates can resolve ``{% static %}``
# without a collectstatic-built manifest (base.py uses whitenoise's manifest
# storage, which raises on missing manifest entries during tests).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# The fastest hasher drastically speeds up user-creation in tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Capture outgoing mail so tests can assert on it (FR-27).
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable migrations noise / speed things up while still exercising constraints.
WHITENOISE_AUTOREFRESH = True

DJANGO_LOG_LEVEL = "WARNING"
