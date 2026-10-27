"""Admin registration for reviews."""

from __future__ import annotations

from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("cafe", "author", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("cafe__name", "author__email")
