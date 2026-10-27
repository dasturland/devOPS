"""django-filter filter sets for cafes (FR-23)."""

from __future__ import annotations

import django_filters

from apps.cafes.models import Cafe


class CafeFilter(django_filters.FilterSet):
    """Filter cafes by name / address substring and active flag."""

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    address = django_filters.CharFilter(field_name="address", lookup_expr="icontains")

    class Meta:
        model = Cafe
        fields = ["name", "address", "is_active"]
