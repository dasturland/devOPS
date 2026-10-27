"""DRF router assembling all domain viewsets (§8.2)."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from apps.api.views import (
    CafeViewSet,
    ReservationViewSet,
    ReviewViewSet,
    TableViewSet,
    ZoneViewSet,
)

router = DefaultRouter()
router.register("cafes", CafeViewSet, basename="cafe")
router.register("zones", ZoneViewSet, basename="zone")
router.register("tables", TableViewSet, basename="table")
router.register("reservations", ReservationViewSet, basename="reservation")
router.register("reviews", ReviewViewSet, basename="review")
