"""Development settings: SQLite, console email, verbose logging (FR-27, NFR-11)."""

from __future__ import annotations

from .base import BASE_DIR, env, env_bool
from .base import *  # noqa: F401,F403

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104 - dev only

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Email is printed to the console during local development (FR-27).
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Make logging chatty locally unless explicitly overridden.
DJANGO_LOG_LEVEL = env("DJANGO_LOG_LEVEL", "DEBUG")
