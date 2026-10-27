"""Custom user model with a role field (FR-01, FR-06, §3.3)."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.managers import UserManager


class Role(models.TextChoices):
    """RBAC roles (FR-06)."""

    ADMIN = "ADMIN", "Administrator"
    MANAGER = "MANAGER", "Kafe menejeri"
    CUSTOMER = "CUSTOMER", "Mijoz"
    WAITER = "WAITER", "Ofitsiant"


class User(AbstractUser):
    """Platform user authenticated by email with an explicit role."""

    email = models.EmailField("email", unique=True)
    role = models.CharField(
        "rol",
        max_length=16,
        choices=Role.choices,
        default=Role.CUSTOMER,
        db_index=True,
    )
    phone = models.CharField("telefon", max_length=32, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()  # type: ignore[assignment]

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        indexes = [models.Index(fields=["role"], name="accounts_user_role_idx")]

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_customer(self) -> bool:
        return self.role == Role.CUSTOMER

    @property
    def is_waiter(self) -> bool:
        return self.role == Role.WAITER
