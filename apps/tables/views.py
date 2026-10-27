"""Web views for table CRUD (FR-10, FR-07)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.cafes.models import Zone
from apps.tables.forms import TableForm
from apps.tables.services import create_table

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def _can_manage(user, zone: Zone) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == "ADMIN":
        return True
    return user.role == "MANAGER" and zone.cafe.manager_id == user.pk


def table_list(request: HttpRequest, zone_id: int) -> HttpResponse:
    """List the tables of a zone."""
    zone = get_object_or_404(Zone.objects.select_related("cafe"), pk=zone_id)
    tables = zone.tables.all()
    return render(
        request,
        "tables/list.html",
        {"zone": zone, "tables": tables, "can_manage": _can_manage(request.user, zone)},
    )


@login_required
@require_http_methods(["GET", "POST"])
def table_create(request: HttpRequest, zone_id: int) -> HttpResponse:
    """Create a table in a zone (owner manager / admin only)."""
    zone = get_object_or_404(Zone.objects.select_related("cafe"), pk=zone_id)
    if not _can_manage(request.user, zone):
        raise PermissionDenied
    form = TableForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_table(request.user, zone, form.cleaned_data)
        messages.success(request, "Stol qo'shildi.")
        return redirect("tables:list", zone_id=zone.pk)
    return render(request, "tables/form.html", {"form": form, "zone": zone})
