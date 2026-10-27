"""Core views: health-check, home page and custom error handlers (§10)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.core.services import check_database

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@require_GET
def health_check(request: HttpRequest) -> JsonResponse:
    """Return the service / database health as JSON (FR-25, §10.3)."""
    database_ok = check_database()
    if database_ok:
        return JsonResponse({"status": "ok", "database": "ok"}, status=200)
    return JsonResponse({"status": "error", "database": "down"}, status=503)


def home(request: HttpRequest) -> HttpResponse:
    """Render the public landing page."""
    return render(request, "core/home.html")


def handler403(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Render the branded 403 page (FR-29)."""
    return render(request, "errors/403.html", status=403)


def handler404(
    request: HttpRequest, exception: Exception | None = None
) -> HttpResponse:
    """Render the branded 404 page (FR-29)."""
    return render(request, "errors/404.html", status=404)


def handler500(request: HttpRequest) -> HttpResponse:
    """Render the branded 500 page (FR-29)."""
    return render(request, "errors/500.html", status=500)
