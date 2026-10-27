"""Web view, health-check and permission integration tests (FR-02..FR-25)."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db


def test_health_check_ok(client):
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_home_page_renders(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200


def test_register_view_creates_user(client):
    response = client.post(
        reverse("accounts:register"),
        {
            "first_name": "Ali",
            "email": "ali@example.com",
            "password": "pass12345xyz",
            "password_confirm": "pass12345xyz",
        },
    )
    assert response.status_code == 302
    from django.contrib.auth import get_user_model

    assert get_user_model().objects.filter(email="ali@example.com").exists()


def test_login_logout_flow(client):
    CustomerFactory(email="log@example.com", password="pass12345")
    response = client.post(
        reverse("accounts:login"),
        {"email": "log@example.com", "password": "pass12345"},
    )
    assert response.status_code == 302
    logout = client.post(reverse("accounts:logout"))
    assert logout.status_code == 302


def test_login_bad_credentials(client):
    CustomerFactory(email="log2@example.com", password="pass12345")
    response = client.post(
        reverse("accounts:login"),
        {"email": "log2@example.com", "password": "wrong"},
    )
    assert response.status_code == 200
    assert "noto'g'ri" in response.content.decode().lower()


def test_profile_requires_login(client):
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302


def test_cafe_list_renders(client, cafe):
    response = client.get(reverse("cafes:list"))
    assert response.status_code == 200
    assert cafe.name.encode() in response.content


def test_my_reservations_requires_login(client):
    response = client.get(reverse("reservations:my"))
    assert response.status_code == 302


def test_manager_schedule_denied_for_customer(client):
    customer = CustomerFactory(password="pass12345")
    client.force_login(customer)
    response = client.get(reverse("reservations:schedule"))
    assert response.status_code == 403


def test_search_view_renders(client):
    response = client.get(reverse("reservations:search"))
    assert response.status_code == 200
