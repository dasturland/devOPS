"""Reservation model (FR-12..FR-18, §3.6).

Note on ``time_range``: the PostgreSQL ``ExclusionConstraint`` relies on a
``tsrange`` column. Because the project also supports SQLite for local
development and tests (NFR-11), the range column and the exclusion constraint
are added by a *conditional* migration guarded by ``connection.vendor`` rather
than being declared as a model field here. The Python-side overlap check in
``services.py`` provides the equivalent guarantee on SQLite.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.core.models import TimeStampedModel
from apps.reservations.managers import ReservationManager
from apps.tables.models import Table


class ReservationStatus(models.TextChoices):
    """Reservation lifecycle states (FR-16)."""

    PENDING = "PENDING", "Kutilmoqda"
    CONFIRMED = "CONFIRMED", "Tasdiqlangan"
    COMPLETED = "COMPLETED", "Yakunlangan"
    CANCELLED = "CANCELLED", "Bekor qilingan"
    REJECTED = "REJECTED", "Rad etilgan"
    NO_SHOW = "NO_SHOW", "Kelmadi"


class Reservation(TimeStampedModel):
    """A customer booking of a table for a time window (FR-12)."""

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="mijoz",
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="stol",
    )
    start_time = models.DateTimeField("boshlanish vaqti", db_index=True)
    duration_minutes = models.PositiveSmallIntegerField("davomiylik (daqiqa)", default=120)
    guests_count = models.PositiveSmallIntegerField("odam soni")
    status = models.CharField(
        "holat",
        max_length=12,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
        db_index=True,
    )
    note = models.TextField("izoh", blank=True)

    objects = ReservationManager()

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ["-start_time"]
        constraints = [
            models.CheckConstraint(condition=Q(guests_count__gte=1), name="res_guests_gte_1"),
            models.CheckConstraint(condition=Q(duration_minutes__gte=30), name="res_duration_min"),
        ]
        indexes = [
            models.Index(fields=["table", "start_time"], name="res_table_start_idx"),
            models.Index(fields=["status"], name="res_status_idx"),
            models.Index(fields=["customer", "status"], name="res_customer_status_idx"),
        ]

    def __str__(self) -> str:
        return f"Bron #{self.pk} ({self.get_status_display()})"

    @property
    def end_time(self) -> datetime:
        """Return the reservation end time (FR-13 overlap calculation)."""
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def cafe(self):  # noqa: ANN201 - Cafe, avoid circular import in hints
        """Return the owning cafe (convenience accessor)."""
        return self.table.zone.cafe
