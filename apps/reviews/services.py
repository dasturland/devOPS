"""Review services (FR-21, §6.3)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from apps.core.exceptions import PermissionError, ValidationError
from apps.core.models import AuditAction
from apps.core.services import record_audit
from apps.reservations.models import Reservation, ReservationStatus
from apps.reviews.models import Review

if TYPE_CHECKING:
    from apps.accounts.models import User

logger = logging.getLogger(__name__)


def create_review(
    customer: User, reservation: Reservation, rating: int, comment: str = ""
) -> Review:
    """Create a review for a completed reservation, once, by its owner (FR-21)."""
    if reservation.customer_id != customer.pk:
        raise PermissionError("Faqat bron egasi sharh qoldira oladi.")
    if reservation.status != ReservationStatus.COMPLETED:
        raise ValidationError("Sharh faqat yakunlangan bron uchun qoldiriladi.")
    if not 1 <= int(rating) <= 5:
        raise ValidationError("Baho 1 dan 5 gacha bo'lishi kerak.")
    if Review.objects.filter(reservation=reservation).exists():
        raise ValidationError("Bu bron uchun sharh allaqachon qoldirilgan.")

    review = Review.objects.create(
        reservation=reservation,
        cafe=reservation.table.zone.cafe,
        author=customer,
        rating=int(rating),
        comment=comment,
    )
    record_audit(customer, AuditAction.CREATE, review)
    logger.info("review %s created for reservation %s", review.pk, reservation.pk)
    return review
