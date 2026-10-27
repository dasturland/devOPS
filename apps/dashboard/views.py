"""Dashboard views (FR-20, FR-22, FR-07)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.dashboard.services import admin_stats

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@login_required
def dashboard_home(request: HttpRequest) -> HttpResponse:
    """Role-aware dashboard landing page."""
    user = request.user
    if getattr(user, "role", None) == "ADMIN" or user.is_superuser:
        return redirect_admin(request)
    if getattr(user, "role", None) in {"MANAGER", "WAITER"}:
        return redirect("reservations:schedule")
    return redirect("reservations:my")


@login_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    """Admin statistics dashboard with a date filter (FR-22)."""
    user = request.user
    if getattr(user, "role", None) != "ADMIN" and not user.is_superuser:
        raise PermissionDenied
    return redirect_admin(request)


def redirect_admin(request: HttpRequest) -> HttpResponse:
    """Render the admin statistics page (shared by home / admin views)."""
    today = timezone.localdate()
    date_from = _parse_date(request.GET.get("date_from"), today - timedelta(days=7))
    date_to = _parse_date(request.GET.get("date_to"), today)
    stats = admin_stats(date_from, date_to)
    chart_data = {
        "labels": list(stats["by_status"].keys()),
        "values": list(stats["by_status"].values()),
    }
    context = {
        "stats": stats,
        "date_from": date_from,
        "date_to": date_to,
        "chart_data_json": json.dumps(chart_data),
    }
    return render(request, "dashboard/admin.html", context)


def _parse_date(value: str | None, default):  # noqa: ANN001, ANN202
    if not value:
        return default
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return default
