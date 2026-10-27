"""Behavioural coverage for serializers, mixins, services and forms.

These exercise the lowest-coverage modules (accounts.serializers, core.mixins,
cafes.services, tables.services, reviews.services and the model forms) through
their real behaviour rather than bare imports.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from apps.accounts.serializers import RegistrationSerializer, UserSerializer
from apps.cafes.forms import CafeForm, ZoneForm
from apps.cafes.models import Zone
from apps.cafes.services import (
    cafe_average_rating,
    create_cafe,
    manage_zone,
    update_cafe,
)
from apps.core.exceptions import PermissionError, ValidationError
from apps.core.mixins import (
    AdminRequiredMixin,
    CustomerRequiredMixin,
    ManagerRequiredMixin,
)
from apps.reservations.models import ReservationStatus
from apps.reviews.forms import ReviewForm
from apps.reviews.models import Review
from apps.reviews.services import create_review
from apps.tables.forms import TableForm
from apps.tables.models import Table
from apps.tables.services import create_table, ensure_unique_number
from tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# accounts.serializers
# ---------------------------------------------------------------------------
def test_user_serializer_exposes_expected_fields(customer_user):
    data = UserSerializer(customer_user).data
    assert data["email"] == customer_user.email
    assert data["role"] == "CUSTOMER"
    # ``role`` is declared read-only.
    assert "role" in UserSerializer().Meta.read_only_fields


def test_registration_serializer_rejects_short_password():
    serializer = RegistrationSerializer(
        data={"email": "x@example.com", "password": "short", "first_name": "A"}
    )
    assert not serializer.is_valid()
    assert "password" in serializer.errors


def test_registration_serializer_creates_customer():
    serializer = RegistrationSerializer(
        data={"email": "reg@example.com", "password": "pass12345", "first_name": "Reg"}
    )
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.email == "reg@example.com"
    assert user.role == "CUSTOMER"


# ---------------------------------------------------------------------------
# core.mixins
# ---------------------------------------------------------------------------
class _MixinView:
    """Minimal CBV stand-in exposing the parts the mixin dispatch touches."""

    def __init__(self, user):
        self.request = RequestFactory().get("/")
        self.request.user = user

    def dispatch(self, request, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        return HttpResponse("ok")


def _build(mixin_cls, user):
    bases = (mixin_cls, _MixinView)
    view = type("V", bases, {})(user)
    return view


def test_role_mixin_allows_matching_role(customer_user):
    view = _build(CustomerRequiredMixin, customer_user)
    response = view.dispatch(view.request)
    assert response.status_code == 200


def test_role_mixin_allows_superuser(admin_user):
    view = _build(ManagerRequiredMixin, admin_user)
    response = view.dispatch(view.request)
    assert response.status_code == 200


def test_role_mixin_denies_wrong_role(customer_user):
    view = _build(AdminRequiredMixin, customer_user)
    # AccessMixin.handle_no_permission raises PermissionDenied when the user is
    # authenticated (the default raise_exception stays False), so a forbidden
    # role triggers the exception rather than a redirect.
    with pytest.raises(PermissionDenied):
        view.dispatch(view.request)


def test_role_mixin_denies_anonymous():
    view = _build(CustomerRequiredMixin, AnonymousUser())
    # Anonymous users are not authenticated and raise_exception is False, so the
    # mixin redirects (302) to the login page via redirect_to_login.
    response = view.dispatch(view.request)
    assert response.status_code == 302
    assert isinstance(view, AccessMixin)


# ---------------------------------------------------------------------------
# cafes.services
# ---------------------------------------------------------------------------
def _cafe_payload(manager, **overrides):
    from datetime import time

    data = {
        "manager": manager,
        "name": "Yangi Kafe",
        "address": "Toshkent",
        "phone": "+998900000001",
        "opening_time": time(9, 0),
        "closing_time": time(22, 0),
    }
    data.update(overrides)
    return data


def test_create_cafe_generates_slug(admin_user, manager_user):
    cafe = create_cafe(admin_user, _cafe_payload(manager_user))
    assert cafe.slug == "yangi-kafe"


def test_create_cafe_slug_is_unique(admin_user, manager_user):
    first = create_cafe(admin_user, _cafe_payload(manager_user, name="Takror"))
    second = create_cafe(admin_user, _cafe_payload(manager_user, name="Takror"))
    assert first.slug != second.slug
    assert second.slug.startswith("takror")


def test_create_cafe_rejects_bad_hours(admin_user, manager_user):
    from datetime import time

    with pytest.raises(ValidationError):
        create_cafe(
            admin_user,
            _cafe_payload(manager_user, opening_time=time(22, 0), closing_time=time(9, 0)),
        )


def test_update_cafe_records_changes(admin_user, cafe):
    updated = update_cafe(admin_user, cafe, {"name": "O'zgargan nom"})
    updated.refresh_from_db()
    assert updated.name == "O'zgargan nom"


def test_manage_zone_creates_zone(admin_user, cafe):
    zone = manage_zone(admin_user, cafe, {"name": "Terasa", "zone_type": "TERRACE"})
    assert isinstance(zone, Zone)
    assert zone.cafe_id == cafe.pk


def test_manage_zone_rejects_duplicate_name(admin_user, cafe):
    manage_zone(admin_user, cafe, {"name": "Asosiy"})
    with pytest.raises(ValidationError):
        manage_zone(admin_user, cafe, {"name": "asosiy"})


def test_cafe_average_rating_without_reviews(cafe):
    assert cafe_average_rating(cafe) == 0.0


def test_cafe_average_rating_with_reviews(cafe, table, customer_user, future_start):
    from tests.factories import ReservationFactory

    reservation = ReservationFactory(
        table=table,
        customer=customer_user,
        start_time=future_start,
        status=ReservationStatus.COMPLETED,
    )
    Review.objects.create(reservation=reservation, cafe=cafe, author=customer_user, rating=4)
    assert cafe_average_rating(cafe) == 4.0


# ---------------------------------------------------------------------------
# tables.services
# ---------------------------------------------------------------------------
def test_create_table_persists_record(admin_user, zone):
    table = create_table(admin_user, zone, {"number": "A1", "capacity": 4})
    assert isinstance(table, Table)
    assert table.number == "A1"
    assert table.zone_id == zone.pk


def test_create_table_rejects_zero_capacity(admin_user, zone):
    with pytest.raises(ValidationError):
        create_table(admin_user, zone, {"number": "B2", "capacity": 0})


def test_create_table_rejects_duplicate_number(admin_user, zone):
    create_table(admin_user, zone, {"number": "C3", "capacity": 2})
    with pytest.raises(ValidationError):
        create_table(admin_user, zone, {"number": "C3", "capacity": 2})


def test_ensure_unique_number_excludes_self(cafe, table):
    # Re-checking the same table with its own pk must not raise.
    ensure_unique_number(cafe, table.number, exclude_pk=table.pk)


# ---------------------------------------------------------------------------
# reviews.services
# ---------------------------------------------------------------------------
def _completed_reservation(table, customer, future_start):
    from tests.factories import ReservationFactory

    return ReservationFactory(
        table=table,
        customer=customer,
        start_time=future_start,
        status=ReservationStatus.COMPLETED,
    )


def test_create_review_success(table, customer_user, future_start):
    reservation = _completed_reservation(table, customer_user, future_start)
    review = create_review(customer_user, reservation, 5, "Zo'r")
    assert review.rating == 5
    assert review.cafe_id == table.zone.cafe_id


def test_create_review_requires_owner(table, customer_user, future_start):
    reservation = _completed_reservation(table, customer_user, future_start)
    stranger = CustomerFactory()
    with pytest.raises(PermissionError):
        create_review(stranger, reservation, 5)


def test_create_review_requires_completed(reservation, customer_user):
    assert reservation.status == ReservationStatus.PENDING
    with pytest.raises(ValidationError):
        create_review(customer_user, reservation, 5)


def test_create_review_rejects_second_review(table, customer_user, future_start):
    reservation = _completed_reservation(table, customer_user, future_start)
    create_review(customer_user, reservation, 4)
    with pytest.raises(ValidationError):
        create_review(customer_user, reservation, 3)


# ---------------------------------------------------------------------------
# forms
# ---------------------------------------------------------------------------
def test_cafe_form_rejects_inverted_hours(manager_user):
    form = CafeForm(
        data={
            "manager": manager_user.pk,
            "name": "Form Kafe",
            "address": "Toshkent",
            "phone": "+998900000002",
            "opening_time": "22:00",
            "closing_time": "09:00",
        }
    )
    assert not form.is_valid()
    assert "closing_time" in form.errors


def test_zone_form_valid():
    form = ZoneForm(data={"name": "VIP", "zone_type": "VIP"})
    assert form.is_valid(), form.errors


def test_table_form_rejects_zero_capacity():
    form = TableForm(data={"number": "9", "capacity": 0, "status": "AVAILABLE"})
    assert not form.is_valid()
    assert "capacity" in form.errors


def test_review_form_rejects_out_of_range_rating():
    form = ReviewForm(data={"rating": 9, "comment": "Yomon"})
    assert not form.is_valid()
    assert "rating" in form.errors


def test_review_form_accepts_valid_rating():
    form = ReviewForm(data={"rating": 4, "comment": "Yaxshi"})
    assert form.is_valid(), form.errors
