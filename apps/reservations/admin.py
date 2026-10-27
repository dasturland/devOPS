"""Admin registration for reservations."""

from __future__ import annotations

from django.contrib import admin

from apps.reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "table", "start_time", "status", "guests_count")
    list_filter = ("status",)
    search_fields = ("customer__email", "note")
    date_hierarchy = "start_time"
    autocomplete_fields = ("customer", "table")
