"""Serializers for the accounts app (FR-24)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.services import register_customer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for user records."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "role", "is_active", "date_joined"]


class RegistrationSerializer(serializers.Serializer):
    """Write serializer that registers a new customer (FR-01)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)

    def create(self, validated_data: dict[str, Any]) -> Any:
        return register_customer(validated_data)
