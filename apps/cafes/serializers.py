"""Serializers for the cafes app (FR-24)."""

from __future__ import annotations

from rest_framework import serializers

from apps.cafes.models import Cafe, Zone
from apps.cafes.services import cafe_average_rating


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for seating zones."""

    class Meta:
        model = Zone
        fields = ["id", "cafe", "name", "zone_type"]
        read_only_fields = ["id"]


class CafeSerializer(serializers.ModelSerializer):
    """Serializer for cafes including the computed average rating."""

    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Cafe
        fields = [
            "id",
            "manager",
            "name",
            "slug",
            "address",
            "phone",
            "description",
            "opening_time",
            "closing_time",
            "is_active",
            "average_rating",
        ]
        read_only_fields = ["id", "slug", "average_rating"]

    def get_average_rating(self, obj: Cafe) -> float:
        return cafe_average_rating(obj)
