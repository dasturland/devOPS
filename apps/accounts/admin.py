"""Admin registration for the custom user model (FR-24)."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin for the email-based user model."""

    ordering = ("email",)
    list_display = ("email", "username", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Shaxsiy", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Rol va ruxsatlar",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Sanalar", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "role", "password1", "password2"),
            },
        ),
    )
