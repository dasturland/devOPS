"""Admin registration for cafes and zones."""

from __future__ import annotations

from django.contrib import admin

from apps.cafes.models import Cafe, Zone


class ZoneInline(admin.TabularInline):
    model = Zone
    extra = 0


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "is_active", "opening_time", "closing_time")
    list_filter = ("is_active",)
    search_fields = ("name", "address")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ZoneInline]


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "cafe", "zone_type")
    list_filter = ("zone_type",)
    search_fields = ("name",)
