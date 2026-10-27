"""Cross-cutting services: audit, notifications and the DB health probe (§4)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.core.mail import send_mail
from django.db import connection

from apps.core.models import AuditLog

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.db.models import Model

    from apps.accounts.models import User

logger = logging.getLogger(__name__)


def record_audit(
    actor: User | None,
    action: str,
    instance: Model,
    changes: dict[str, Any] | None = None,
) -> AuditLog:
    """Persist an :class:`~apps.core.models.AuditLog` entry (FR-26)."""
    entry = AuditLog.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        action=action,
        object_type=instance.__class__.__name__,
        object_id=str(instance.pk),
        changes=changes or {},
    )
    logger.info("audit: %s %s#%s", action, instance.__class__.__name__, instance.pk)
    return entry


def send_notification(
    user: AbstractBaseUser | None,
    subject: str,
    message: str,
) -> int:
    """Send an email notification to ``user`` (FR-27).

    Returns the number of successfully delivered messages. In development the
    console backend prints the message; in tests the locmem backend captures it.
    """
    email = getattr(user, "email", None)
    if not email:
        logger.warning("notification skipped: user has no email")
        return 0
    from django.conf import settings

    sent = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
    logger.info("notification sent to %s (subject=%s)", email, subject)
    return sent


def check_database() -> bool:
    """Return ``True`` when ``SELECT 1`` succeeds against the default DB (FR-25)."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 - any DB failure means "down"
        logger.exception("database health check failed")
        return False
    return True
