"""Fast settings for the automated test-suite (NFR-05)."""

from __future__ import annotations

from .base import *  # noqa: F401,F403

DEBUG = False

# In-memory SQLite keeps the suite fast and isolated.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# The fastest hasher drastically speeds up user-creation in tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Capture outgoing mail so tests can assert on it (FR-27).
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable migrations noise / speed things up while still exercising constraints.
WHITENOISE_AUTOREFRESH = True

DJANGO_LOG_LEVEL = "WARNING"
