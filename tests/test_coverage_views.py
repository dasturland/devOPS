"""Behavioural coverage for the tables and reviews web views (FR-10, FR-21)."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.reservations.models import ReservationStatus
from apps.reviews.models import Review
from apps.tables.models import Table
from tests.factories import CustomerFactory, ReservationFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# tables.views
# ---------------------------------------------------------------------------
def test_table_list_renders(client, zone, table):
    response = client.get(reverse("tables:list", args=[zone.pk]))
    assert response.status_code == 200
    assert table.number.encode() in response.content


def test_table_create_requires_login(client, zone):
    response = client.get(reverse("tables:create", args=[zone.pk]))
    assert response.status_code == 302


def test_table_create_denied_for_customer(client, zone):
    client.force_login(CustomerFactory(password="pass12345"))
    response = client.get(reverse("tables:create", args=[zone.pk]))
    assert response.status_code == 403


def test_table_create_allowed_for_owner_manager(client, zone):
    client.force_login(zone.cafe.manager)
    get_response = client.get(reverse("tables:create", args=[zone.pk]))
    assert get_response.status_code == 200
    post_response = client.post(
        reverse("tables:create", args=[zone.pk]),
        {"number": "77", "capacity": 4, "status": "AVAILABLE"},
    )
    assert post_response.status_code == 302
    assert Table.objects.filter(zone=zone, number="77").exists()


def test_table_create_denied_for_other_manager(client, zone):
    from tests.factories import ManagerFactory

    client.force_login(ManagerFactory(password="pass12345"))
    response = client.get(reverse("tables:create", args=[zone.pk]))
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# reviews.views
# ---------------------------------------------------------------------------
def test_create_review_requires_login(client, reservation):
    response = client.get(reverse("reviews:create", args=[reservation.pk]))
    assert response.status_code == 302


def test_create_review_get_renders_form(client, table, customer_user, future_start):
    reservation = ReservationFactory(
        table=table,
        customer=customer_user,
        start_time=future_start,
        status=ReservationStatus.COMPLETED,
    )
    client.force_login(customer_user)
    response = client.get(reverse("reviews:create", args=[reservation.pk]))
    assert response.status_code == 200


def test_create_review_post_saves(client, table, customer_user, future_start):
    reservation = ReservationFactory(
        table=table,
        customer=customer_user,
        start_time=future_start,
        status=ReservationStatus.COMPLETED,
    )
    client.force_login(customer_user)
    response = client.post(
        reverse("reviews:create", args=[reservation.pk]),
        {"rating": 5, "comment": "Ajoyib joy"},
    )
    assert response.status_code == 302
    assert Review.objects.filter(reservation=reservation, rating=5).exists()


def test_create_review_post_on_pending_shows_error(client, reservation):
    client.force_login(reservation.customer)
    response = client.post(
        reverse("reviews:create", args=[reservation.pk]),
        {"rating": 4, "comment": "Hali yakunlanmagan"},
    )
    # The domain error redirects back to "my reservations" without a review.
    assert response.status_code == 302
    assert not Review.objects.filter(reservation=reservation).exists()
