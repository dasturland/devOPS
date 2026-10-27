"""Reservation business logic: search, creation, conflict and state machine.

Covers FR-11..FR-18 and §5, §6 of the design.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from apps.core.exceptions import (
    ConflictError,
    InvalidTransitionError,
    PermissionError,
    ValidationError,
)
from apps.core.models import AuditAction
from apps.core.services import record_audit, send_notification
from apps.reservations.managers import ACTIVE_STATUSES
from apps.reservations.models import Reservation, ReservationStatus
from apps.tables.models import Table

if TYPE_CHECKING:
    from apps.accounts.models import User

logger = logging.getLogger(__name__)

# Minimum notice (hours) required for a customer cancellation (FR-18).
CANCEL_MIN_HOURS = 2

# Legal reservation state transitions (§6.1).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    ReservationStatus.PENDING: {
        ReservationStatus.CONFIRMED,
        ReservationStatus.REJECTED,
        ReservationStatus.CANCELLED,
    },
    ReservationStatus.CONFIRMED: {
        ReservationStatus.COMPLETED,
        ReservationStatus.CANCELLED,
        ReservationStatus.NO_SHOW,
    },
    ReservationStatus.COMPLETED: set(),
    ReservationStatus.CANCELLED: set(),
    ReservationStatus.REJECTED: set(),
    ReservationStatus.NO_SHOW: set(),
}


# ---------------------------------------------------------------------------
# Search (FR-11)
# ---------------------------------------------------------------------------
def _overlaps(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    """Return ``True`` when two half-open intervals overlap (§5.2)."""
    return start1 < end2 and start2 < end1


def search_available_tables(criteria: dict[str, Any]) -> list[Table]:
    """Return tables free for the requested window (FR-11).

    ``criteria`` keys: ``date`` (``datetime.date``), ``start_time``
    (``datetime.time``), ``duration_minutes`` (int), ``guests_count`` (int) and
    optional ``zone`` / ``cafe`` identifiers.
    """
    day: date = criteria["date"]
    start_time = criteria["start_time"]
    duration = int(criteria.get("duration_minutes", 120))
    guests = int(criteria.get("guests_count", 1))

    window_start = timezone.make_aware(datetime.combine(day, start_time))
    window_end = window_start + timedelta(minutes=duration)

    tables = (
        Table.objects.select_related("zone", "zone__cafe")
        .filter(status="AVAILABLE", capacity__gte=guests)
    )
    if criteria.get("zone"):
        tables = tables.filter(zone_id=criteria["zone"])
    if criteria.get("cafe"):
        tables = tables.filter(zone__cafe_id=criteria["cafe"])

    # Prefetch the active reservations that could possibly overlap the day.
    busy = (
        Reservation.objects.filter(
            table__in=tables,
            status__in=ACTIVE_STATUSES,
            start_time__date__in=[day, day - timedelta(days=1), day + timedelta(days=1)],
        )
        .only("table_id", "start_time", "duration_minutes")
    )
    busy_by_table: dict[int, list[Reservation]] = {}
    for reservation in busy:
        busy_by_table.setdefault(reservation.table_id, []).append(reservation)

    available: list[Table] = []
    for table in tables:
        conflicts = any(
            _overlaps(window_start, window_end, r.start_time, r.end_time)
            for r in busy_by_table.get(table.pk, [])
        )
        if not conflicts:
            available.append(table)
    return available


# ---------------------------------------------------------------------------
# Creation (FR-12..FR-15)
# ---------------------------------------------------------------------------
def _validate_window(table: Table, start_time: datetime, duration: int, guests: int) -> None:
    """Validate working hours, past time and capacity (FR-14, FR-15)."""
    now = timezone.now()
    if start_time < now:
        raise ValidationError("Bron vaqti o'tmishda bo'lishi mumkin emas.")

    if guests > table.capacity:
        raise ValidationError(
            "Odam soni stol sig'imidan oshib ketdi "
            f"(sig'im: {table.capacity})."
        )

    cafe = table.zone.cafe
    local_start = timezone.localtime(start_time)
    end_local = local_start + timedelta(minutes=duration)
    start_t = local_start.time()
    end_t = end_local.time()
    # Reservation must fall entirely within the cafe working hours on one day.
    if (
        end_local.date() != local_start.date()
        or start_t < cafe.opening_time
        or end_t > cafe.closing_time
    ):
        raise ValidationError("Tanlangan vaqt kafe ish vaqtidan tashqarida.")


def create_reservation(customer: User, data: dict[str, Any]) -> Reservation:
    """Create a ``PENDING`` reservation with conflict protection (FR-12, FR-13).

    Uses ``transaction.atomic`` + ``select_for_update`` so two concurrent
    requests are serialised; the PostgreSQL exclusion constraint is the final
    guarantee in production while the explicit overlap check protects SQLite.
    """
    table_id = data["table"]
    start_time: datetime = data["start_time"]
    duration = int(data.get("duration_minutes", 120))
    guests = int(data["guests_count"])

    if guests < 1:
        raise ValidationError("Odam soni kamida 1 bo'lishi kerak.")
    if duration < 30:
        raise ValidationError("Davomiylik kamida 30 daqiqa bo'lishi kerak.")

    end_time = start_time + timedelta(minutes=duration)

    with transaction.atomic():
        table = (
            Table.objects.select_related("zone", "zone__cafe").select_for_update().get(pk=table_id)
        )
        _validate_window(table, start_time, duration, guests)

        overlapping = (
            Reservation.objects.select_for_update()
            .filter(table=table, status__in=ACTIVE_STATUSES)
        )
        for existing in overlapping:
            if _overlaps(start_time, end_time, existing.start_time, existing.end_time):
                logger.info("reservation conflict on table %s", table.pk)
                raise ConflictError

        reservation = Reservation.objects.create(
            customer=customer,
            table=table,
            start_time=start_time,
            duration_minutes=duration,
            guests_count=guests,
            note=data.get("note", ""),
            status=ReservationStatus.PENDING,
        )
        record_audit(customer, AuditAction.CREATE, reservation)

    _notify(reservation, "Yangi bron yaratildi", customer)
    manager = reservation.table.zone.cafe.manager
    send_notification(
        manager,
        "Yangi bron keltirildi",
        f"#{reservation.pk} bron tasdiqlashingizni kutmoqda.",
    )
    logger.info("reservation %s created by %s", reservation.pk, customer.pk)
    return reservation


# ---------------------------------------------------------------------------
# State machine (FR-16, FR-17, FR-18, §6)
# ---------------------------------------------------------------------------
def _notify(reservation: Reservation, subject: str, user: User) -> None:
    send_notification(
        user,
        subject,
        f"Bron #{reservation.pk} holati: {reservation.get_status_display()}.",
    )


def transition(reservation: Reservation, target: str, actor: User) -> Reservation:
    """Apply a validated state transition, audit and notify (§6).

    Raises :class:`InvalidTransitionError` for illegal transitions (FR-16).
    """
    current = reservation.status
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidTransitionError(f"'{current}' holatidan '{target}' holatiga o'tib bo'lmaydi.")
    reservation.status = target
    reservation.save(update_fields=["status", "updated_at"])
    record_audit(actor, AuditAction.UPDATE, reservation, {"status": [current, target]})
    _notify(reservation, "Bron holati o'zgardi", reservation.customer)
    logger.info("reservation %s: %s -> %s", reservation.pk, current, target)
    return reservation


def _require_cafe_manager(reservation: Reservation, actor: User) -> None:
    """Ensure ``actor`` manages the reservation's cafe (FR-17, FR-07)."""
    if actor.is_superuser or getattr(actor, "role", None) == "ADMIN":
        return
    manager_id = reservation.table.zone.cafe.manager_id
    allowed_roles = {"MANAGER", "WAITER"}
    if getattr(actor, "role", None) not in allowed_roles or manager_id != actor.pk:
        raise PermissionError("Siz bu kafe bronlarini boshqara olmaysiz.")


def confirm(reservation: Reservation, actor: User) -> Reservation:
    """Manager confirms a pending reservation (FR-17)."""
    _require_cafe_manager(reservation, actor)
    return transition(reservation, ReservationStatus.CONFIRMED, actor)


def reject(reservation: Reservation, actor: User) -> Reservation:
    """Manager rejects a pending reservation (FR-17)."""
    _require_cafe_manager(reservation, actor)
    return transition(reservation, ReservationStatus.REJECTED, actor)


def cancel(reservation: Reservation, actor: User) -> Reservation:
    """Customer cancels their reservation at least 2 hours ahead (FR-18)."""
    if reservation.customer_id != actor.pk and not actor.is_superuser:
        raise PermissionError("Faqat bron egasi uni bekor qila oladi.")
    remaining = reservation.start_time - timezone.now()
    if remaining < timedelta(hours=CANCEL_MIN_HOURS):
        raise ValidationError("Bronni boshlanishiga kamida 2 soat qolganda bekor qilish mumkin.")
    return transition(reservation, ReservationStatus.CANCELLED, actor)


def complete(reservation: Reservation, actor: User) -> Reservation:
    """Staff marks a confirmed reservation as completed (§6)."""
    _require_cafe_manager(reservation, actor)
    return transition(reservation, ReservationStatus.COMPLETED, actor)


def mark_no_show(reservation: Reservation, actor: User) -> Reservation:
    """Staff marks a confirmed reservation as a no-show (§6)."""
    _require_cafe_manager(reservation, actor)
    return transition(reservation, ReservationStatus.NO_SHOW, actor)


# ---------------------------------------------------------------------------
# Query helpers used by views / API
# ---------------------------------------------------------------------------
def reservations_for_customer(user: User) -> QuerySet[Reservation]:
    """Return a customer's reservations (FR-19)."""
    return Reservation.objects.for_customer(user)


def daily_schedule(cafe, day: date) -> QuerySet[Reservation]:
    """Return a cafe's reservations for a given day (FR-20)."""
    return Reservation.objects.for_cafe(cafe).on_date(day).order_by("start_time")
