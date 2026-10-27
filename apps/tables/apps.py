"""App configuration for the tables app."""

from __future__ import annotations

from django.apps import AppConfig


class TablesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tables"
    label = "tables"
    verbose_name = "Stollar"
