"""DRF viewsets assembling the domain logic under /api/v1/ (§8.2)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsManagerOfCafe
from apps.cafes.filters import CafeFilter
from apps.cafes.models import Cafe, Zone
from apps.cafes.serializers import CafeSerializer, ZoneSerializer
from apps.core.exceptions import DomainError
from apps.reservations import services as reservation_services
from apps.reservations.filters import ReservationFilter
from apps.reservations.models import Reservation
from apps.reservations.serializers import (
    AvailabilityQuerySerializer,
    ReservationCreateSerializer,
    ReservationSerializer,
)
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer
from apps.reviews.services import create_review
from apps.tables.models import Table
from apps.tables.serializers import TableSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class CafeViewSet(viewsets.ModelViewSet):
    """CRUD for cafes (FR-08, FR-24). Reads are public."""

    queryset = Cafe.objects.select_related("manager").all()
    serializer_class = CafeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsManagerOfCafe]
    filterset_class = CafeFilter
    search_fields = ["name", "address"]
    ordering_fields = ["name", "created_at"]
    lookup_field = "slug"


class ZoneViewSet(viewsets.ModelViewSet):
    """CRUD for zones (FR-09, FR-24)."""

    queryset = Zone.objects.select_related("cafe").all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsManagerOfCafe]
    filterset_fields = ["cafe", "zone_type"]


class TableViewSet(viewsets.ModelViewSet):
    """CRUD for tables plus the availability search (FR-10, FR-11, FR-24)."""

    queryset = Table.objects.select_related("zone", "zone__cafe").all()
    serializer_class = TableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsManagerOfCafe]
    filterset_fields = ["zone", "status"]

    @extend_schema(
        parameters=[AvailabilityQuerySerializer],
        responses=TableSerializer(many=True),
        description="Berilgan sana, vaqt va odam soniga ko'ra bo'sh stollarni qaytaradi.",
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def availability(self, request: Request) -> Response:
        """Return tables that are free for the requested window (FR-11)."""
        query = AvailabilityQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        tables = reservation_services.search_available_tables(query.validated_data)
        return Response(TableSerializer(tables, many=True).data)


class ReservationViewSet(viewsets.ModelViewSet):
    """Reservations with state-machine action endpoints (FR-12..FR-18, FR-24)."""

    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ReservationFilter
    ordering_fields = ["start_time", "created_at"]

    def get_queryset(self):  # noqa: ANN201
        user = self.request.user
        base = Reservation.objects.with_related()
        if user.is_superuser or getattr(user, "role", None) == "ADMIN":
            return base
        if getattr(user, "role", None) in {"MANAGER", "WAITER"}:
            return base.filter(table__zone__cafe__manager=user)
        return base.filter(customer=user)

    def get_serializer_class(self):  # noqa: ANN201
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = reservation_services.create_reservation(
            request.user, serializer.validated_data
        )
        return Response(
            ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED
        )

    def _run_action(self, request: Request, pk: str | None, func) -> Response:  # noqa: ANN001
        reservation = self.get_object()
        try:
            func(reservation, request.user)
        except DomainError as exc:
            return Response({"detail": exc.message}, status=exc.status_code)
        return Response(ReservationSerializer(reservation).data)

    @action(detail=True, methods=["post"])
    def confirm(self, request: Request, pk: str | None = None) -> Response:
        return self._run_action(request, pk, reservation_services.confirm)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk: str | None = None) -> Response:
        return self._run_action(request, pk, reservation_services.reject)

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk: str | None = None) -> Response:
        return self._run_action(request, pk, reservation_services.cancel)

    @action(detail=True, methods=["post"])
    def complete(self, request: Request, pk: str | None = None) -> Response:
        return self._run_action(request, pk, reservation_services.complete)

    @action(detail=True, methods=["post"], url_path="no-show")
    def no_show(self, request: Request, pk: str | None = None) -> Response:
        return self._run_action(request, pk, reservation_services.mark_no_show)


class ReviewViewSet(viewsets.ModelViewSet):
    """Reviews, creatable only by the owning customer (FR-21, FR-24)."""

    queryset = Review.objects.select_related("cafe", "author", "reservation").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["cafe", "rating"]

    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        reservation_id = request.data.get("reservation")
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")
        try:
            reservation = Reservation.objects.with_related().get(pk=reservation_id)
            review = create_review(request.user, reservation, rating, comment)
        except Reservation.DoesNotExist:
            return Response({"detail": "Bron topilmadi."}, status=404)
        except DomainError as exc:
            return Response({"detail": exc.message}, status=exc.status_code)
        return Response(
            ReviewSerializer(review).data, status=status.HTTP_201_CREATED
        )


__all__ = [
    "CafeViewSet",
    "ZoneViewSet",
    "TableViewSet",
    "ReservationViewSet",
    "ReviewViewSet",
]
