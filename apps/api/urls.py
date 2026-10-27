"""API URL configuration: versioned routes + OpenAPI schema/docs (FR-24, §8.3)."""

from __future__ import annotations

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from apps.api.routers import router

app_name = "api"

urlpatterns = [
    path("v1/", include((router.urls, "v1"))),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="docs",
    ),
]
