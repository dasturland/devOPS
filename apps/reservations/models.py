"""Reservation model (FR-12..FR-18, §3.6).

Note on ``time_range``: the PostgreSQL ``ExclusionConstraint`` relies on a
materialised ``tstzrange`` column (``time_range``) because an inline expression
such as ``start_time + duration_minutes * interval`` is only ``STABLE`` (it
depends on the session ``TimeZone``/DST) and therefore cannot appear in a GiST
index/exclusion expression. The column is populated in :meth:`Reservation.save`.
Because the project also supports SQLite for local development and tests
(NFR-11), the column is added on every backend but is only *populated* on
PostgreSQL; on SQLite it stays ``NULL`` (psycopg2 range objects cannot be bound
as SQLite parameters) and the exclusion constraint is skipped, so the
Python-side overlap check in ``services.py`` provides the equivalent guarantee.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.postgres.fields import DateTimeRangeField
from django.db import models, router
from django.db.models import Q
from psycopg2.extras import DateTimeTZRange

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
    time_range = DateTimeRangeField(null=True, blank=True, editable=False)

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

    def save(self, *args: object, **kwargs: object) -> None:
        """Materialise ``time_range`` from ``start_time``/``duration`` (FR-13).

        The stored ``tstzrange`` is what the PostgreSQL exclusion constraint
        indexes, so it must be kept in sync on every write. The value is only
        populated on PostgreSQL; on SQLite the column stays ``NULL`` (psycopg2
        range objects cannot be bound as SQLite parameters) and the equivalent
        guarantee is provided by the overlap check in ``services.py``.
        """
        connection = router.db_for_write(type(self), instance=self)
        if self.start_time is not None and self._db_is_postgres(connection):
            self.time_range = DateTimeTZRange(self.start_time, self.end_time, bounds="[)")
        super().save(*args, **kwargs)

    @staticmethod
    def _db_is_postgres(alias: str) -> bool:
        from django.db import connections

        return connections[alias].vendor == "postgresql"

    @property
    def end_time(self) -> datetime:
        """Return the reservation end time (FR-13 overlap calculation)."""
        return self.start_time + timedelta(minutes=self.duration_minutes)

    @property
    def cafe(self):  # noqa: ANN201 - Cafe, avoid circular import in hints
        """Return the owning cafe (convenience accessor)."""
        return self.table.zone.cafe
