"""QuerySet and manager for reservations (§3.6)."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.cafes.models import Cafe

# Statuses considered "active" for conflict detection (§5.2).
ACTIVE_STATUSES = ("PENDING", "CONFIRMED")


class ReservationQuerySet(models.QuerySet):
    """Chainable queries with N+1-safe ``select_related`` (NFR-03)."""

    def with_related(self) -> ReservationQuerySet:
        return self.select_related(
            "customer", "table", "table__zone", "table__zone__cafe"
        )

    def active(self) -> ReservationQuerySet:
        return self.filter(status__in=ACTIVE_STATUSES)

    def for_customer(self, user: User) -> ReservationQuerySet:
        return self.filter(customer=user).with_related()

    def for_cafe(self, cafe: Cafe) -> ReservationQuerySet:
        return self.filter(table__zone__cafe=cafe).with_related()

    def on_date(self, day: date) -> ReservationQuerySet:
        return self.filter(start_time__date=day)


class ReservationManager(models.Manager.from_queryset(ReservationQuerySet)):  # type: ignore[misc]
    """Default manager exposing the custom queryset methods."""
