"""Review model (FR-21, §3.7)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.cafes.models import Cafe
from apps.core.models import TimeStampedModel
from apps.reservations.models import Reservation


class Review(TimeStampedModel):
    """A 1-5 star review tied to a completed reservation (FR-21)."""

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="bron",
    )
    cafe = models.ForeignKey(
        Cafe,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="kafe",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="muallif",
    )
    rating = models.PositiveSmallIntegerField("baho")
    comment = models.TextField("izoh", blank=True)

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_1_5",
            )
        ]
        indexes = [models.Index(fields=["cafe", "rating"], name="review_cafe_rating_idx")]

    def __str__(self) -> str:
        return f"{self.cafe.name} ({self.rating}/5)"
