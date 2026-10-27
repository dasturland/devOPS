"""Serializers for the reservations app (FR-24)."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """Read serializer for reservations with computed end time."""

    end_time = serializers.DateTimeField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "customer",
            "table",
            "start_time",
            "end_time",
            "duration_minutes",
            "guests_count",
            "status",
            "status_display",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "customer", "status", "created_at"]


class ReservationCreateSerializer(serializers.Serializer):
    """Write serializer that feeds ``create_reservation`` (FR-12)."""

    table = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(min_value=30, default=120)
    guests_count = serializers.IntegerField(min_value=1)
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        return super().to_internal_value(data)


class AvailabilityQuerySerializer(serializers.Serializer):
    """Query serializer for the availability endpoint (FR-11)."""

    date = serializers.DateField()
    start_time = serializers.TimeField()
    duration_minutes = serializers.IntegerField(min_value=30, default=120)
    guests_count = serializers.IntegerField(min_value=1, default=1)
    zone = serializers.IntegerField(required=False)
    cafe = serializers.IntegerField(required=False)
