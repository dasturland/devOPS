"""Web views for cafe and zone CRUD (FR-08, FR-09, FR-07)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.cafes.forms import CafeForm, ZoneForm
from apps.cafes.models import Cafe
from apps.cafes.services import cafe_average_rating, create_cafe, manage_zone

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def _can_manage(user, cafe: Cafe | None = None) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == "ADMIN":
        return True
    if user.role != "MANAGER":
        return False
    return cafe is None or cafe.manager_id == user.pk


def cafe_list(request: HttpRequest) -> HttpResponse:
    """Public list of active cafes (FR-08, FR-23)."""
    cafes = Cafe.objects.select_related("manager").all()
    query = request.GET.get("q", "").strip()
    if query:
        cafes = cafes.filter(name__icontains=query)
    return render(request, "cafes/list.html", {"cafes": cafes, "query": query})


def cafe_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Cafe detail page with average rating and zones."""
    cafe = get_object_or_404(
        Cafe.objects.select_related("manager").prefetch_related("zones"),
        slug=slug,
    )
    context = {
        "cafe": cafe,
        "average_rating": cafe_average_rating(cafe),
        "can_manage": _can_manage(request.user, cafe),
    }
    return render(request, "cafes/detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def cafe_create(request: HttpRequest) -> HttpResponse:
    """Create a cafe (ADMIN / MANAGER only)."""
    if not _can_manage(request.user):
        raise PermissionDenied
    form = CafeForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        cafe = create_cafe(request.user, form.cleaned_data)
        messages.success(request, "Kafe yaratildi.")
        return redirect("cafes:detail", slug=cafe.slug)
    return render(request, "cafes/form.html", {"form": form, "title": "Yangi kafe"})


@login_required
@require_http_methods(["GET", "POST"])
def zone_create(request: HttpRequest, slug: str) -> HttpResponse:
    """Add a zone to a cafe (owner manager / admin only)."""
    cafe = get_object_or_404(Cafe, slug=slug)
    if not _can_manage(request.user, cafe):
        raise PermissionDenied
    form = ZoneForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        manage_zone(request.user, cafe, form.cleaned_data)
        messages.success(request, "Zona qo'shildi.")
        return redirect("cafes:detail", slug=cafe.slug)
    return render(request, "cafes/form.html", {"form": form, "title": "Yangi zona"})
