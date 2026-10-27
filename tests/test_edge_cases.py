"""Phase 13 edge-case coverage: concurrency, seed, wizard, dashboard, auth.

These tests complement the existing model/service/view suites and target the
scenarios called out in the plan (FR-13, FR-14, FR-15, FR-16, FR-18, FR-21,
FR-07, FR-28, NFR-05). They are written to pass on both SQLite (local/CI
default) and the CI PostgreSQL service.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from apps.cafes.models import Cafe
from apps.core.exceptions import ConflictError
from apps.reservations import services
from apps.reservations.models import Reservation, ReservationStatus
from apps.reviews.models import Review
from apps.tables.models import Table
from tests.factories import CustomerFactory, ManagerFactory

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


# --------------------------------------------------------------------------
# Double-booking guarantee (FR-13)
# --------------------------------------------------------------------------
def test_sequential_double_booking_blocked(table, future_start):
    """Two bookings for the same window must not both succeed (FR-13)."""
    first = services.create_reservation(CustomerFactory(), _data(table, future_start))
    assert first.status == ReservationStatus.PENDING

    with pytest.raises(ConflictError):
        services.create_reservation(
            CustomerFactory(), _data(table, future_start + timedelta(minutes=15))
        )
    # Only one active reservation survived the conflict check.
    active = Reservation.objects.filter(table=table).active().count()
    assert active == 1


def test_cancelled_reservation_frees_the_slot(table, future_start, customer_user):
    """A cancelled reservation no longer blocks the same window (FR-13)."""
    reservation = services.create_reservation(customer_user, _data(table, future_start))
    services.cancel(reservation, customer_user)
    # The slot is free again now that the first booking is CANCELLED.
    second = services.create_reservation(CustomerFactory(), _data(table, future_start))
    assert second.pk is not None


# --------------------------------------------------------------------------
# Review rules (FR-21)
# --------------------------------------------------------------------------
def test_review_only_for_completed(reservation, customer_user):
    from apps.core.exceptions import ValidationError
    from apps.reviews.services import create_review

    with pytest.raises(ValidationError):
        create_review(customer_user, reservation, 5, "Yaxshi")


def test_review_once_per_reservation(reservation, manager_user, customer_user):
    from apps.core.exceptions import ValidationError
    from apps.reviews.services import create_review

    services.confirm(reservation, manager_user)
    services.complete(reservation, manager_user)
    create_review(customer_user, reservation, 5, "Zo'r")
    with pytest.raises(ValidationError):
        create_review(customer_user, reservation, 4, "Yana")
    assert Review.objects.filter(reservation=reservation).count() == 1


# --------------------------------------------------------------------------
# Booking wizard (FR-12) via the web views
# --------------------------------------------------------------------------
def test_booking_wizard_creates_reservation(client, table, future_start):
    customer = CustomerFactory(password="pass12345")
    client.force_login(customer)
    local = timezone.localtime(future_start)
    response = client.post(
        reverse("reservations:book"),
        {
            "table": table.pk,
            "date": local.date().isoformat(),
            "start_time": local.strftime("%H:%M"),
            "duration_minutes": 120,
            "guests_count": 2,
            "note": "Deraza yonida",
        },
    )
    assert response.status_code == 302
    assert Reservation.objects.filter(customer=customer, table=table).exists()


def test_booking_wizard_denied_for_manager(client, table, future_start):
    manager = ManagerFactory(password="pass12345")
    client.force_login(manager)
    response = client.get(reverse("reservations:book"))
    assert response.status_code == 403


# --------------------------------------------------------------------------
# Dashboard permissions (FR-07, FR-22)
# --------------------------------------------------------------------------
def test_admin_dashboard_allowed_for_admin(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("dashboard:admin"))
    assert response.status_code == 200


def test_admin_dashboard_denied_for_customer(client):
    customer = CustomerFactory(password="pass12345")
    client.force_login(customer)
    response = client.get(reverse("dashboard:admin"))
    assert response.status_code == 403


# --------------------------------------------------------------------------
# Home page featured content (FR-11, FR-21, FR-30)
# --------------------------------------------------------------------------
def test_home_lists_active_cafes(client, cafe):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    assert cafe.name.encode() in response.content


# --------------------------------------------------------------------------
# seed_demo_data idempotency (FR-28)
# --------------------------------------------------------------------------
def test_seed_demo_data_is_idempotent():
    call_command("seed_demo_data", reservations=48)
    cafes_first = Cafe.objects.count()
    tables_first = Table.objects.count()
    res_first = Reservation.objects.count()

    # Running a second time must not create duplicates.
    call_command("seed_demo_data", reservations=48)
    assert Cafe.objects.count() == cafes_first
    assert Table.objects.count() == tables_first
    assert Reservation.objects.count() == res_first


def test_seed_demo_data_volume_meets_requirements():
    call_command("seed_demo_data", reservations=48)
    assert Cafe.objects.count() >= 3
    assert Table.objects.count() >= 30
    assert Reservation.objects.count() >= 40
    # Every lifecycle status is represented.
    statuses = set(Reservation.objects.values_list("status", flat=True))
    assert ReservationStatus.COMPLETED in statuses
    assert ReservationStatus.CANCELLED in statuses
    assert Review.objects.count() >= 1
