"""Admin registration for core models (FR-26)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin

from apps.core.models import AuditLog

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only audit log view in the Django admin (FR-26)."""

    list_display = ("created_at", "action", "object_type", "object_id", "actor")
    list_filter = ("action", "object_type")
    search_fields = ("object_type", "object_id")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: object | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: object | None = None
    ) -> bool:
        return False
