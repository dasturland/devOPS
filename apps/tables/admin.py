"""Admin registration for tables."""

from __future__ import annotations

from django.contrib import admin

from apps.tables.models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("number", "zone", "capacity", "status")
    list_filter = ("status", "zone__cafe")
    search_fields = ("number",)
