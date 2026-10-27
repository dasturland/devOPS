"""Model constraint and property tests (FR-10, FR-15, FR-21)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.db.utils import DataError

from apps.core.models import AuditAction, AuditLog
from tests.factories import (
    ReservationFactory,
    ReviewFactory,
    TableFactory,
    UserFactory,
    ZoneFactory,
)

pytestmark = pytest.mark.django_db


def test_user_str_is_email():
    user = UserFactory(email="a@b.com")
    assert str(user) == "a@b.com"


def test_user_role_properties():
    user = UserFactory(role="CUSTOMER")
    assert user.is_customer
    assert not user.is_admin


def test_table_capacity_constraint(zone):
    with pytest.raises((IntegrityError, DataError)):
        TableFactory(zone=zone, capacity=0)


def test_table_unique_number_per_zone(zone):
    TableFactory(zone=zone, number="5")
    with pytest.raises(IntegrityError):
        TableFactory(zone=zone, number="5")


def test_zone_unique_name_per_cafe(cafe):
    ZoneFactory(cafe=cafe, name="Zal A")
    with pytest.raises(IntegrityError):
        ZoneFactory(cafe=cafe, name="Zal A")


def test_reservation_end_time_property(table, customer_user, future_start):
    reservation = ReservationFactory(
        table=table, customer=customer_user, start_time=future_start, duration_minutes=90
    )
    assert reservation.end_time == future_start + timedelta(minutes=90)


def test_reservation_cafe_property(reservation):
    assert reservation.cafe == reservation.table.zone.cafe


def test_review_rating_constraint(reservation):
    reservation.status = "COMPLETED"
    reservation.save()
    with pytest.raises(IntegrityError):
        ReviewFactory(reservation=reservation, rating=6)


def test_audit_log_str():
    entry = AuditLog.objects.create(action=AuditAction.CREATE, object_type="Cafe", object_id="1")
    assert "CREATE" in str(entry)
