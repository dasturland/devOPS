"""Reservation service edge cases and the state machine (FR-11..FR-18)."""

from __future__ import annotations

from datetime import time, timedelta

import pytest
from django.utils import timezone

from apps.core.exceptions import (
    ConflictError,
    InvalidTransitionError,
    PermissionError,
    ValidationError,
)
from apps.reservations import services
from apps.reservations.models import ReservationStatus
from tests.factories import CustomerFactory, ReservationFactory, TableFactory

pytestmark = pytest.mark.django_db


def _data(table, start, **kwargs):
    base = {
        "table": table.pk,
        "start_time": start,
        "duration_minutes": 120,
        "guests_count": 2,
    }
    base.update(kwargs)
    return base


def test_create_reservation_success(table, customer_user, future_start):
    reservation = services.create_reservation(customer_user, _data(table, future_start))
    assert reservation.status == ReservationStatus.PENDING
    assert reservation.customer == customer_user


def test_create_reservation_past_rejected(table, customer_user):
    past = timezone.now() - timedelta(hours=1)
    with pytest.raises(ValidationError):
        services.create_reservation(customer_user, _data(table, past))


def test_create_reservation_over_capacity_rejected(table, customer_user, future_start):
    with pytest.raises(ValidationError):
        services.create_reservation(
            customer_user, _data(table, future_start, guests_count=table.capacity + 1)
        )


def test_create_reservation_off_hours_rejected(cafe, customer_user):
    cafe.opening_time = time(9, 0)
    cafe.closing_time = time(17, 0)
    cafe.save()
    table = TableFactory(zone__cafe=cafe, capacity=4)
    # 20:00 tomorrow is outside 09:00-17:00.
    start = timezone.localtime(timezone.now()).replace(
        hour=20, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)
    with pytest.raises(ValidationError):
        services.create_reservation(customer_user, _data(table, start))


def test_create_reservation_conflict_rejected(table, customer_user, future_start):
    services.create_reservation(customer_user, _data(table, future_start))
    other = CustomerFactory()
    overlapping = future_start + timedelta(minutes=30)
    with pytest.raises(ConflictError):
        services.create_reservation(other, _data(table, overlapping))


def test_non_overlapping_same_table_allowed(table, customer_user, future_start):
    services.create_reservation(customer_user, _data(table, future_start))
    later = future_start + timedelta(hours=3)
    second = services.create_reservation(CustomerFactory(), _data(table, later))
    assert second.pk is not None


def test_search_available_tables_excludes_busy(table, customer_user, future_start):
    services.create_reservation(customer_user, _data(table, future_start))
    criteria = {
        "date": timezone.localtime(future_start).date(),
        "start_time": timezone.localtime(future_start).time(),
        "duration_minutes": 120,
        "guests_count": 2,
    }
    available = services.search_available_tables(criteria)
    assert table not in available


def test_search_available_tables_includes_free(table, future_start):
    criteria = {
        "date": timezone.localtime(future_start).date(),
        "start_time": timezone.localtime(future_start).time(),
        "duration_minutes": 120,
        "guests_count": 2,
    }
    available = services.search_available_tables(criteria)
    assert table in available


# ----- state machine -----
def test_confirm_by_manager(reservation, manager_user):
    services.confirm(reservation, manager_user)
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.CONFIRMED


def test_confirm_by_foreign_manager_denied(reservation):
    from tests.factories import ManagerFactory

    other_manager = ManagerFactory()
    with pytest.raises(PermissionError):
        services.confirm(reservation, other_manager)


def test_invalid_transition_rejected(reservation, manager_user):
    services.confirm(reservation, manager_user)
    services.complete(reservation, manager_user)
    # COMPLETED is terminal.
    with pytest.raises(InvalidTransitionError):
        services.transition(reservation, ReservationStatus.PENDING, manager_user)


def test_cancel_within_two_hours_rejected(table, customer_user):
    soon = timezone.now() + timedelta(hours=1)
    # Create directly to bypass creation validation for the 2h rule test.
    reservation = ReservationFactory(table=table, customer=customer_user, start_time=soon)
    with pytest.raises(ValidationError):
        services.cancel(reservation, customer_user)


def test_cancel_more_than_two_hours_allowed(reservation, customer_user):
    services.cancel(reservation, customer_user)
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.CANCELLED


def test_cancel_by_other_user_denied(reservation):
    other = CustomerFactory()
    with pytest.raises(PermissionError):
        services.cancel(reservation, other)


def test_reject_notifies_customer(reservation, manager_user, mailoutbox):
    services.reject(reservation, manager_user)
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.REJECTED
    assert len(mailoutbox) >= 1


def test_no_show_from_confirmed(reservation, manager_user):
    services.confirm(reservation, manager_user)
    services.mark_no_show(reservation, manager_user)
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.NO_SHOW


def test_daily_schedule_returns_reservations(reservation, cafe):
    day = timezone.localtime(reservation.start_time).date()
    schedule = services.daily_schedule(cafe, day)
    assert reservation in list(schedule)
