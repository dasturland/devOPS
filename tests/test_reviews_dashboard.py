"""Review service and dashboard statistics tests (FR-21, FR-22)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.cafes.services import cafe_average_rating
from apps.core.exceptions import PermissionError, ValidationError
from apps.dashboard import services as dashboard_services
from apps.reviews.services import create_review
from tests.factories import CustomerFactory, ReservationFactory

pytestmark = pytest.mark.django_db


def _completed(table, customer, start):
    return ReservationFactory(
        table=table, customer=customer, start_time=start, status="COMPLETED"
    )


def test_create_review_requires_completed(reservation, customer_user):
    with pytest.raises(ValidationError):
        create_review(customer_user, reservation, 5, "ok")


def test_create_review_wrong_author(table, customer_user, future_start):
    completed = _completed(table, customer_user, future_start)
    other = CustomerFactory()
    with pytest.raises(PermissionError):
        create_review(other, completed, 5, "ok")


def test_create_review_once(table, customer_user, future_start):
    completed = _completed(table, customer_user, future_start)
    create_review(customer_user, completed, 5, "zo'r")
    with pytest.raises(ValidationError):
        create_review(customer_user, completed, 4, "again")


def test_cafe_average_rating(table, customer_user, future_start, cafe):
    completed = _completed(table, customer_user, future_start)
    create_review(customer_user, completed, 4, "yaxshi")
    assert cafe_average_rating(cafe) == 4.0


def test_admin_stats_aggregates(reservation):
    today = timezone.localdate()
    stats = dashboard_services.admin_stats(today - timedelta(days=2), today + timedelta(days=2))
    assert stats["total_reservations"] >= 1
    assert "PENDING" in stats["by_status"]


def test_cancellation_rate(table, customer_user, future_start):
    ReservationFactory(table=table, customer=customer_user, start_time=future_start, status="CANCELLED")
    today = timezone.localdate()
    rate = dashboard_services.cancellation_rate(today - timedelta(days=2), today + timedelta(days=2))
    assert rate == 100.0


def test_busiest_tables(reservation):
    today = timezone.localdate()
    rows = dashboard_services.busiest_tables(today - timedelta(days=2), today + timedelta(days=2))
    assert rows and rows[0]["count"] >= 1
