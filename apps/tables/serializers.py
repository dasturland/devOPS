"""Serializers for the tables app (FR-24)."""

from __future__ import annotations

from rest_framework import serializers

from apps.tables.models import Table


class TableSerializer(serializers.ModelSerializer):
    """Serializer for tables."""

    cafe_id = serializers.IntegerField(source="zone.cafe_id", read_only=True)

    class Meta:
        model = Table
        fields = ["id", "zone", "cafe_id", "number", "capacity", "status"]
        read_only_fields = ["id", "cafe_id"]
