"""Web views: 3-step booking wizard, my-reservations, manager schedule (§7)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Callable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.core.exceptions import DomainError
from apps.reservations import services
from apps.reservations.forms import AvailabilitySearchForm, ReservationConfirmForm
from apps.reservations.models import Reservation

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@require_http_methods(["GET", "POST"])
def search_view(request: HttpRequest) -> HttpResponse:
    """Step 1 & 2: search availability and list free tables (FR-11)."""
    form = AvailabilitySearchForm(request.GET or None)
    tables: list = []
    searched = False
    if request.GET and form.is_valid():
        searched = True
        criteria = {
            "date": form.cleaned_data["date"],
            "start_time": form.cleaned_data["start_time"],
            "duration_minutes": form.cleaned_data["duration_minutes"],
            "guests_count": form.cleaned_data["guests_count"],
        }
        tables = services.search_available_tables(criteria)
    return render(
        request,
        "reservations/search.html",
        {"form": form, "tables": tables, "searched": searched},
    )


@login_required
@require_http_methods(["GET", "POST"])
def book_view(request: HttpRequest) -> HttpResponse:
    """Step 3: confirm the selected table and create the reservation (FR-12)."""
    if getattr(request.user, "role", None) != "CUSTOMER" and not request.user.is_superuser:
        raise PermissionDenied
    source = request.POST if request.method == "POST" else request.GET
    form = ReservationConfirmForm(source or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        start_time = timezone.make_aware(
            datetime.combine(data["date"], data["start_time"])
        )
        try:
            reservation = services.create_reservation(
                request.user,
                {
                    "table": data["table"],
                    "start_time": start_time,
                    "duration_minutes": data["duration_minutes"],
                    "guests_count": data["guests_count"],
                    "note": data["note"],
                },
            )
        except DomainError as exc:
            messages.error(request, exc.message)
            return redirect("reservations:search")
        messages.success(request, "Bron yaratildi va tasdiqlash kutilmoqda.")
        return redirect("reservations:my")
    return render(request, "reservations/book.html", {"form": form})


@login_required
def my_reservations_view(request: HttpRequest) -> HttpResponse:
    """Paginated, filterable list of the customer's reservations (FR-19)."""
    qs = services.reservations_for_customer(request.user)
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "reservations/my.html",
        {"page_obj": page, "status": status or ""},
    )


@login_required
def manager_schedule_view(request: HttpRequest) -> HttpResponse:
    """Manager daily schedule for their cafe (FR-20)."""
    user = request.user
    if getattr(user, "role", None) not in {"MANAGER", "WAITER", "ADMIN"} and not user.is_superuser:
        raise PermissionDenied
    cafe = user.managed_cafes.first()
    day_str = request.GET.get("date")
    day = (
        datetime.strptime(day_str, "%Y-%m-%d").date()
        if day_str
        else timezone.localdate()
    )
    reservations = services.daily_schedule(cafe, day) if cafe else []
    return render(
        request,
        "reservations/schedule.html",
        {"cafe": cafe, "day": day, "reservations": reservations},
    )


def _action_view(action: Callable[[Reservation, object], Reservation], success: str):
    """Build a POST-only view that applies a state-machine action."""

    @login_required
    @require_http_methods(["POST"])
    def view(request: HttpRequest, pk: int) -> HttpResponse:
        reservation = get_object_or_404(
            Reservation.objects.with_related(), pk=pk
        )
        try:
            action(reservation, request.user)
        except DomainError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, success)
        referer = request.META.get("HTTP_REFERER")
        return redirect(referer) if referer else redirect("reservations:my")

    return view


confirm_view = _action_view(services.confirm, "Bron tasdiqlandi.")
reject_view = _action_view(services.reject, "Bron rad etildi.")
cancel_view = _action_view(services.cancel, "Bron bekor qilindi.")
complete_view = _action_view(services.complete, "Bron yakunlandi.")
no_show_view = _action_view(services.mark_no_show, "Mijoz kelmadi deb belgilandi.")
