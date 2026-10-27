"""Cafe and Zone models (FR-08, FR-09, §3.4)."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ZoneType(models.TextChoices):
    """Zone categories (FR-09)."""

    HALL = "HALL", "Zal"
    TERRACE = "TERRACE", "Terrasa"
    VIP = "VIP", "VIP"


class Cafe(TimeStampedModel):
    """A cafe managed by a ``MANAGER`` user (FR-08)."""

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_cafes",
        limit_choices_to={"role": "MANAGER"},
        verbose_name="menejer",
    )
    name = models.CharField("nom", max_length=160)
    slug = models.SlugField("slug", unique=True)
    address = models.CharField("manzil", max_length=255)
    phone = models.CharField("telefon", max_length=32)
    description = models.TextField("tavsif", blank=True)
    opening_time = models.TimeField("ochilish vaqti")
    closing_time = models.TimeField("yopilish vaqti")
    image = models.ImageField("rasm", upload_to="cafes/", blank=True)
    is_active = models.BooleanField("faol", default=True, db_index=True)

    class Meta:
        verbose_name = "Kafe"
        verbose_name_plural = "Kafelar"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="cafe_name_idx"),
            models.Index(fields=["is_active"], name="cafe_is_active_idx"),
        ]

    def __str__(self) -> str:
        return self.name


class Zone(TimeStampedModel):
    """A seating zone that belongs to a cafe (FR-09)."""

    cafe = models.ForeignKey(
        Cafe,
        on_delete=models.CASCADE,
        related_name="zones",
        verbose_name="kafe",
    )
    name = models.CharField("nom", max_length=80)
    zone_type = models.CharField(
        "zona turi", max_length=12, choices=ZoneType.choices, default=ZoneType.HALL
    )

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonalar"
        ordering = ["cafe", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["cafe", "name"], name="uniq_zone_name_per_cafe"
            )
        ]

    def __str__(self) -> str:
        return f"{self.cafe.name} / {self.name}"
