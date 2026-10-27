"""Core services and exception tests (FR-25, FR-26, FR-27)."""

from __future__ import annotations

from unittest import mock

import pytest

from apps.core import services
from apps.core.exceptions import ConflictError, DomainError, ValidationError
from apps.core.models import AuditAction, AuditLog
from tests.factories import CafeFactory, CustomerFactory

pytestmark = pytest.mark.django_db


def test_record_audit_creates_entry(admin_user):
    cafe = CafeFactory()
    entry = services.record_audit(admin_user, AuditAction.CREATE, cafe, {"name": ["a", "b"]})
    assert AuditLog.objects.filter(pk=entry.pk).exists()
    assert entry.object_type == "Cafe"


def test_send_notification_delivers(mailoutbox):
    user = CustomerFactory(email="notify@example.com")
    sent = services.send_notification(user, "Subject", "Body")
    assert sent == 1
    assert mailoutbox[0].to == ["notify@example.com"]


def test_send_notification_without_email():
    assert services.send_notification(None, "s", "b") == 0


def test_check_database_ok():
    assert services.check_database() is True


def test_check_database_failure():
    with mock.patch("apps.core.services.connection") as conn:
        conn.cursor.side_effect = RuntimeError("down")
        assert services.check_database() is False


def test_domain_error_default_message():
    assert ValidationError().message
    assert ConflictError().message
    assert isinstance(ValidationError(), DomainError)
