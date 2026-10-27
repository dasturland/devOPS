"""Development settings: SQLite, console email, verbose logging (FR-27, NFR-11)."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env, env_bool, env_list

DEBUG = env_bool("DEBUG", True)

# "localhost" / "127.0.0.1" cover local work; extra hosts (e.g. a container
# bind address) can be added via the ALLOWED_HOSTS env var without binding to
# every interface in source (avoids Bandit B104).
ALLOWED_HOSTS = ["localhost", "127.0.0.1", *env_list("ALLOWED_HOSTS")]

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
