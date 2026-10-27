"""Domain exceptions and the DRF exception handler (§10.1).

These exceptions carry user facing Uzbek messages and are translated to the
appropriate HTTP status code by :func:`drf_exception_handler` for the API and
rendered inline by the web views.
"""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler


class DomainError(Exception):
    """Base class for all business-rule violations."""

    default_message = "Amaliyotni bajarishda xatolik yuz berdi."
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class ValidationError(DomainError):
    """A business validation rule failed (e.g. off-hours, past time)."""

    default_message = "Yuborilgan ma'lumotlar noto'g'ri."
    status_code = status.HTTP_400_BAD_REQUEST


class ConflictError(DomainError):
    """A uniqueness / booking conflict was detected (FR-13)."""

    default_message = "Tanlangan stol ushbu vaqt uchun allaqachon band."
    status_code = status.HTTP_409_CONFLICT


class InvalidTransitionError(DomainError):
    """An illegal reservation state transition was requested (FR-16)."""

    default_message = "Ushbu holat o'tishiga ruxsat yo'q."
    status_code = status.HTTP_409_CONFLICT


class PermissionError(DomainError):  # noqa: A001 - intentional domain name
    """The actor is not allowed to perform the action (FR-07)."""

    default_message = "Ushbu amalni bajarishga ruxsatingiz yo'q."
    status_code = status.HTTP_403_FORBIDDEN


def drf_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Translate :class:`DomainError` subclasses into JSON error responses."""
    if isinstance(exc, DomainError):
        return Response({"detail": exc.message}, status=exc.status_code)
    return drf_default_handler(exc, context)
