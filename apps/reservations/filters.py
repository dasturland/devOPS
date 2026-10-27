"""django-filter filter sets for reservations (FR-19, FR-23)."""

from __future__ import annotations

import django_filters

from apps.reservations.models import Reservation


class ReservationFilter(django_filters.FilterSet):
    """Filter reservations by status, cafe and date range."""

    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    cafe = django_filters.NumberFilter(field_name="table__zone__cafe_id")
    date = django_filters.DateFilter(field_name="start_time", lookup_expr="date")
    date_from = django_filters.DateFilter(field_name="start_time", lookup_expr="date__gte")
    date_to = django_filters.DateFilter(field_name="start_time", lookup_expr="date__lte")

    class Meta:
        model = Reservation
        fields = ["status", "cafe", "date"]
