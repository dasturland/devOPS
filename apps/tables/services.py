"""Table services (FR-10)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.cafes.models import Cafe, Zone
from apps.core.exceptions import ValidationError
from apps.core.models import AuditAction
from apps.core.services import record_audit
from apps.tables.models import Table

if TYPE_CHECKING:
    from apps.accounts.models import User


def ensure_unique_number(cafe: Cafe, number: str, exclude_pk: int | None = None) -> None:
    """Raise when ``number`` is already used by another table in ``cafe`` (FR-10)."""
    qs = Table.objects.filter(zone__cafe=cafe, number=number)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    if qs.exists():
        raise ValidationError(
            f"'{number}' raqamli stol ushbu kafeda allaqachon mavjud."
        )


def create_table(actor: User, zone: Zone, data: dict[str, Any]) -> Table:
    """Create a table enforcing capacity and per-cafe number uniqueness (FR-10)."""
    number = str(data.get("number", "")).strip()
    capacity = int(data.get("capacity", 0))
    if capacity < 1:
        raise ValidationError("Sig'im kamida 1 bo'lishi kerak.")
    ensure_unique_number(zone.cafe, number)
    table = Table.objects.create(
        zone=zone,
        number=number,
        capacity=capacity,
        status=data.get("status", "AVAILABLE"),
    )
    record_audit(actor, AuditAction.CREATE, table)
    return table
