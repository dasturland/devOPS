"""Cafe and zone services (FR-08, FR-09, FR-21)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models import Avg
from django.utils.text import slugify

from apps.cafes.models import Cafe, Zone
from apps.core.exceptions import ValidationError
from apps.core.models import AuditAction
from apps.core.services import record_audit

if TYPE_CHECKING:
    from apps.accounts.models import User


def _unique_slug(name: str) -> str:
    """Return a slug derived from ``name`` that is unique across cafes."""
    base = slugify(name) or "cafe"
    slug = base
    index = 2
    while Cafe.objects.filter(slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug


def create_cafe(actor: User, data: dict[str, Any]) -> Cafe:
    """Create a cafe, generating a slug when one is not supplied (FR-08)."""
    data = dict(data)
    if not data.get("slug"):
        data["slug"] = _unique_slug(data.get("name", ""))
    if data["opening_time"] >= data["closing_time"]:
        raise ValidationError("Ochilish vaqti yopilish vaqtidan oldin bo'lishi kerak.")
    cafe = Cafe.objects.create(**data)
    record_audit(actor, AuditAction.CREATE, cafe)
    return cafe


def update_cafe(actor: User, cafe: Cafe, data: dict[str, Any]) -> Cafe:
    """Update an existing cafe (FR-08)."""
    changes: dict[str, Any] = {}
    for field, value in data.items():
        old = getattr(cafe, field)
        if old != value:
            changes[field] = [str(old), str(value)]
            setattr(cafe, field, value)
    cafe.full_clean(exclude=["slug"])
    cafe.save()
    if changes:
        record_audit(actor, AuditAction.UPDATE, cafe, changes)
    return cafe


def manage_zone(actor: User, cafe: Cafe, data: dict[str, Any]) -> Zone:
    """Create a zone under a cafe, enforcing unique names (FR-09)."""
    name = data.get("name", "").strip()
    if Zone.objects.filter(cafe=cafe, name__iexact=name).exists():
        raise ValidationError("Ushbu kafeda bunday nomli zona allaqachon mavjud.")
    zone = Zone.objects.create(
        cafe=cafe, name=name, zone_type=data.get("zone_type", "HALL")
    )
    record_audit(actor, AuditAction.CREATE, zone)
    return zone


def cafe_average_rating(cafe: Cafe) -> float:
    """Return the average review rating for a cafe, or ``0.0`` (FR-21)."""
    result = cafe.reviews.aggregate(avg=Avg("rating"))
    return round(result["avg"] or 0.0, 2)
