"""DRF API endpoint tests (FR-11, FR-12, FR-17, FR-24)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.reservations.models import ReservationStatus
from tests.factories import CustomerFactory, ReservationFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_schema_endpoint(api_client):
    response = api_client.get("/api/schema/")
    assert response.status_code == 200


def test_docs_endpoint(api_client):
    response = api_client.get("/api/docs/")
    assert response.status_code == 200


def test_cafe_list_public(api_client, cafe):
    response = api_client.get("/api/v1/cafes/")
    assert response.status_code == 200


def test_availability_endpoint(api_client, table, future_start):
    api_client.force_authenticate(CustomerFactory())
    params = {
        "date": timezone.localtime(future_start).date().isoformat(),
        "start_time": timezone.localtime(future_start).time().strftime("%H:%M"),
        "duration_minutes": 120,
        "guests_count": 2,
    }
    response = api_client.get("/api/v1/tables/availability/", params)
    assert response.status_code == 200
    assert any(t["id"] == table.pk for t in response.json())


def test_create_reservation_api(api_client, table, future_start):
    customer = CustomerFactory()
    api_client.force_authenticate(customer)
    payload = {
        "table": table.pk,
        "start_time": future_start.isoformat(),
        "duration_minutes": 120,
        "guests_count": 2,
    }
    response = api_client.post("/api/v1/reservations/", payload, format="json")
    assert response.status_code == 201
    assert response.json()["status"] == ReservationStatus.PENDING


def test_reservation_list_scoped_to_customer(api_client, reservation):
    other = CustomerFactory()
    api_client.force_authenticate(other)
    response = api_client.get("/api/v1/reservations/")
    assert response.status_code == 200
    assert response.json()["count"] == 0


def test_confirm_action_by_manager(api_client, reservation, manager_user):
    api_client.force_authenticate(manager_user)
    response = api_client.post(f"/api/v1/reservations/{reservation.pk}/confirm/")
    assert response.status_code == 200
    assert response.json()["status"] == ReservationStatus.CONFIRMED


def test_cancel_within_two_hours_conflict(api_client, table, customer_user):
    soon = timezone.now() + timedelta(hours=1)
    reservation = ReservationFactory(table=table, customer=customer_user, start_time=soon)
    api_client.force_authenticate(customer_user)
    response = api_client.post(f"/api/v1/reservations/{reservation.pk}/cancel/")
    assert response.status_code == 400


def test_unauthenticated_reservation_list_denied(api_client):
    response = api_client.get("/api/v1/reservations/")
    assert response.status_code in (401, 403)
