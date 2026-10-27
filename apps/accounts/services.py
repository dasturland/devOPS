"""Account services: registration and password management (FR-01, FR-04, FR-05)."""

from __future__ import annotations

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.accounts.models import Role, User
from apps.core.exceptions import ValidationError
from apps.core.services import send_notification

logger = logging.getLogger(__name__)

UserModel = get_user_model()


def register_customer(data: dict[str, Any]) -> User:
    """Create a new ``CUSTOMER`` account (FR-01).

    ``data`` must contain ``email``, ``password`` and ``first_name``; ``username``
    and ``phone`` are optional.
    """
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    if not email or not password:
        raise ValidationError("Email va parol kiritilishi shart.")
    if UserModel.objects.filter(email__iexact=email).exists():
        raise ValidationError("Bunday email allaqachon ro'yxatdan o'tgan.")

    user: User = UserModel.objects.create_user(
        email=email,
        password=password,
        username=data.get("username") or email,
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        phone=data.get("phone", ""),
        role=Role.CUSTOMER,
    )
    logger.info("new customer registered: %s", email)
    return user


def change_password(user: User, old_password: str, new_password: str) -> None:
    """Change a user's password after verifying the current one (FR-04)."""
    if not user.check_password(old_password):
        raise ValidationError("Joriy parol noto'g'ri.")
    user.set_password(new_password)
    user.save(update_fields=["password"])
    logger.info("password changed for %s", user.email)


def issue_password_reset(email: str) -> str | None:
    """Email a password-reset link; never reveal whether the email exists (FR-05).

    Returns the generated token when the user exists (useful for tests), otherwise
    ``None``. Regardless of the return value callers must show the same message.
    """
    email = (email or "").strip().lower()
    user = UserModel.objects.filter(email__iexact=email).first()
    if user is None:
        logger.info("password reset requested for unknown email")
        return None

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = f"/accounts/reset/{uid}/{token}/"
    send_notification(
        user,
        subject="Parolni tiklash",
        message=(
            "Parolingizni tiklash uchun quyidagi havoladan foydalaning:\n"
            f"{reset_path}"
        ),
    )
    return token


def confirm_password_reset(uidb64: str, token: str, new_password: str) -> None:
    """Set a new password using a one-time reset token (FR-05)."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist) as exc:
        raise ValidationError("Tiklash havolasi yaroqsiz.") from exc

    if not default_token_generator.check_token(user, token):
        raise ValidationError("Tiklash havolasi muddati tugagan yoki yaroqsiz.")

    user.set_password(new_password)
    user.save(update_fields=["password"])
    logger.info("password reset confirmed for %s", user.email)
