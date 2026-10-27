"""factory_boy factories for the test-suite (NFR-05)."""

from __future__ import annotations

from datetime import time, timedelta

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.cafes.models import Cafe, Zone, ZoneType
from apps.reservations.models import Reservation, ReservationStatus
from apps.reviews.models import Review
from apps.tables.models import Table

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda obj: obj.email)
    first_name = "Test"
    role = "CUSTOMER"

    @factory.post_generation
    def password(self, create, extracted, **kwargs):  # noqa: ANN001, ANN002
        self.set_password(extracted or "pass12345")
        if create:
            self.save()


class AdminFactory(UserFactory):
    role = "ADMIN"
    is_staff = True
    is_superuser = True


class ManagerFactory(UserFactory):
    role = "MANAGER"


class CustomerFactory(UserFactory):
    role = "CUSTOMER"


class CafeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cafe

    manager = factory.SubFactory(ManagerFactory)
    name = factory.Sequence(lambda n: f"Kafe {n}")
    slug = factory.Sequence(lambda n: f"kafe-{n}")
    address = "Toshkent"
    phone = "+998900000000"
    opening_time = time(8, 0)
    closing_time = time(23, 0)


class ZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Zone

    cafe = factory.SubFactory(CafeFactory)
    name = factory.Sequence(lambda n: f"Zona {n}")
    zone_type = ZoneType.HALL


class TableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Table

    zone = factory.SubFactory(ZoneFactory)
    number = factory.Sequence(lambda n: str(n + 1))
    capacity = 4
    status = "AVAILABLE"


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    customer = factory.SubFactory(CustomerFactory)
    table = factory.SubFactory(TableFactory)
    start_time = factory.LazyFunction(
        lambda: timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        + timedelta(days=1)
    )
    duration_minutes = 120
    guests_count = 2
    status = ReservationStatus.PENDING


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    reservation = factory.SubFactory(ReservationFactory)
    cafe = factory.LazyAttribute(lambda obj: obj.reservation.table.zone.cafe)
    author = factory.LazyAttribute(lambda obj: obj.reservation.customer)
    rating = 5
    comment = "Ajoyib!"
