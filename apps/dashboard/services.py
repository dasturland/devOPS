"""Dashboard statistics computed from live data (FR-20, FR-22, §4)."""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Count

from apps.cafes.models import Cafe
from apps.reservations.models import Reservation, ReservationStatus


def admin_stats(date_from: date, date_to: date) -> dict[str, Any]:
    """Return platform-wide statistics for a date range (FR-22)."""
    qs = Reservation.objects.filter(
        start_time__date__gte=date_from, start_time__date__lte=date_to
    )
    total = qs.count()
    by_status = {
        row["status"]: row["count"]
        for row in qs.values("status").annotate(count=Count("id"))
    }
    return {
        "total_reservations": total,
        "by_status": by_status,
        "cancellation_rate": cancellation_rate(date_from, date_to),
        "busiest_tables": busiest_tables(date_from, date_to),
        "total_cafes": Cafe.objects.count(),
    }


def manager_daily_schedule(cafe: Cafe, day: date) -> list[Reservation]:
    """Return a cafe's reservations for one day, ordered by time (FR-20)."""
    return list(
        Reservation.objects.for_cafe(cafe).on_date(day).order_by("start_time")
    )


def cancellation_rate(date_from: date, date_to: date) -> float:
    """Return the cancellation percentage for a date range (FR-22)."""
    qs = Reservation.objects.filter(
        start_time__date__gte=date_from, start_time__date__lte=date_to
    )
    total = qs.count()
    if total == 0:
        return 0.0
    cancelled = qs.filter(
        status__in=[ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW]
    ).count()
    return round(cancelled / total * 100, 2)


def busiest_tables(date_from: date, date_to: date, limit: int = 5) -> list[dict[str, Any]]:
    """Return the most-reserved tables for a date range (FR-22)."""
    rows = (
        Reservation.objects.filter(
            start_time__date__gte=date_from, start_time__date__lte=date_to
        )
        .values("table_id", "table__number")
        .annotate(count=Count("id"))
        .order_by("-count")[:limit]
    )
    return [
        {"table_id": r["table_id"], "number": r["table__number"], "count": r["count"]}
        for r in rows
    ]
