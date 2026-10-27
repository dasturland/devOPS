"""Table model (FR-10, §3.5)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from apps.cafes.models import Cafe, Zone
from apps.core.models import TimeStampedModel


class TableStatus(models.TextChoices):
    """Table availability states (FR-10)."""

    AVAILABLE = "AVAILABLE", "Mavjud"
    INACTIVE = "INACTIVE", "Faol emas"


class Table(TimeStampedModel):
    """A physical table belonging to a zone (FR-10)."""

    zone = models.ForeignKey(
        Zone,
        on_delete=models.CASCADE,
        related_name="tables",
        verbose_name="zona",
    )
    number = models.CharField("raqam", max_length=16)
    capacity = models.PositiveSmallIntegerField("sig'im")
    status = models.CharField(
        "holat",
        max_length=12,
        choices=TableStatus.choices,
        default=TableStatus.AVAILABLE,
    )

    class Meta:
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"
        ordering = ["zone", "number"]
        constraints = [
            models.CheckConstraint(condition=Q(capacity__gte=1), name="table_capacity_gte_1"),
            models.UniqueConstraint(fields=["zone", "number"], name="uniq_table_number_per_zone"),
        ]
        indexes = [models.Index(fields=["zone", "status"], name="table_zone_status_idx")]

    def __str__(self) -> str:
        return f"{self.zone} / stol {self.number}"

    @property
    def cafe(self) -> Cafe:
        """Return the owning cafe (convenience accessor)."""
        return self.zone.cafe
