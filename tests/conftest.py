"""Shared pytest fixtures (NFR-05)."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from tests.factories import (
    AdminFactory,
    CafeFactory,
    CustomerFactory,
    ManagerFactory,
    ReservationFactory,
    TableFactory,
    ZoneFactory,
)


@pytest.fixture
def admin_user(db):
    return AdminFactory()


@pytest.fixture
def manager_user(db):
    return ManagerFactory()


@pytest.fixture
def customer_user(db):
    return CustomerFactory()


@pytest.fixture
def cafe(db, manager_user):
    return CafeFactory(manager=manager_user)


@pytest.fixture
def zone(db, cafe):
    return ZoneFactory(cafe=cafe)


@pytest.fixture
def table(db, zone):
    return TableFactory(zone=zone, capacity=4)


@pytest.fixture
def future_start(db):
    """A timezone-aware start time tomorrow at noon."""
    return (
        timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        + timedelta(days=1)
    )


@pytest.fixture
def reservation(db, table, customer_user, future_start):
    return ReservationFactory(
        table=table, customer=customer_user, start_time=future_start
    )
