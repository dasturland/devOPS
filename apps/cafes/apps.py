"""App configuration for the cafes app."""

from __future__ import annotations

from django.apps import AppConfig


class CafesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cafes"
    label = "cafes"
    verbose_name = "Kafelar"
