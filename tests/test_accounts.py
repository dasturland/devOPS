"""Account services, manager and permission tests (FR-01..FR-07)."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.accounts import services
from apps.accounts.permissions import (
    IsAdmin,
    IsCustomer,
    IsManager,
    IsOwnerOrReadOnly,
)
from apps.core.exceptions import ValidationError
from tests.factories import CustomerFactory

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="x")


def test_create_superuser_sets_flags():
    admin = User.objects.create_superuser(email="root@example.com", password="pass12345")
    assert admin.is_superuser and admin.is_staff and admin.role == "ADMIN"


def test_register_customer_creates_account():
    user = services.register_customer(
        {"email": "New@Example.com", "password": "pass12345", "first_name": "Ali"}
    )
    assert user.email == "new@example.com"
    assert user.role == "CUSTOMER"
    assert user.check_password("pass12345")


def test_register_duplicate_email_rejected():
    services.register_customer(
        {"email": "dup@example.com", "password": "pass12345", "first_name": "A"}
    )
    with pytest.raises(ValidationError):
        services.register_customer(
            {"email": "dup@example.com", "password": "pass12345", "first_name": "B"}
        )


def test_change_password_wrong_old_rejected():
    user = CustomerFactory(password="old12345")
    with pytest.raises(ValidationError):
        services.change_password(user, "wrong", "new12345")


def test_change_password_success():
    user = CustomerFactory(password="old12345")
    services.change_password(user, "old12345", "new12345")
    user.refresh_from_db()
    assert user.check_password("new12345")


def test_password_reset_unknown_email_returns_none():
    assert services.issue_password_reset("nobody@example.com") is None


def test_password_reset_flow(mailoutbox):
    user = CustomerFactory(email="reset@example.com", password="old12345")
    token = services.issue_password_reset("reset@example.com")
    assert token is not None
    assert len(mailoutbox) == 1
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    services.confirm_password_reset(uid, token, "brandnew123")
    user.refresh_from_db()
    assert user.check_password("brandnew123")


def test_confirm_reset_bad_token_rejected():
    user = CustomerFactory()
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    with pytest.raises(ValidationError):
        services.confirm_password_reset(uid, "bad-token", "brandnew123")


class _Req:
    def __init__(self, user, method="GET"):
        self.user = user
        self.method = method


def test_is_admin_permission(admin_user, customer_user):
    perm = IsAdmin()
    assert perm.has_permission(_Req(admin_user), None)
    assert not perm.has_permission(_Req(customer_user), None)


def test_is_manager_permission(manager_user, customer_user):
    perm = IsManager()
    assert perm.has_permission(_Req(manager_user), None)
    assert not perm.has_permission(_Req(customer_user), None)


def test_is_customer_permission(customer_user, admin_user):
    perm = IsCustomer()
    assert perm.has_permission(_Req(customer_user), None)
    assert not perm.has_permission(_Req(admin_user), None)


def test_is_owner_or_read_only(reservation, customer_user):
    perm = IsOwnerOrReadOnly()
    assert perm.has_object_permission(_Req(customer_user, "GET"), None, reservation)
    assert perm.has_object_permission(_Req(reservation.customer, "DELETE"), None, reservation)
    other = CustomerFactory()
    assert not perm.has_object_permission(_Req(other, "DELETE"), None, reservation)
