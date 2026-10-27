"""Serializers for the reviews app (FR-24)."""

from __future__ import annotations

from rest_framework import serializers

from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews."""

    class Meta:
        model = Review
        fields = [
            "id",
            "reservation",
            "cafe",
            "author",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "cafe", "author", "created_at"]
