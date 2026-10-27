"""Web views for leaving reviews (FR-21)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.core.exceptions import DomainError
from apps.reservations.models import Reservation
from apps.reviews.forms import ReviewForm
from apps.reviews.services import create_review

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from apps.accounts.models import User


@login_required
@require_http_methods(["GET", "POST"])
def create_review_view(request: HttpRequest, reservation_id: int) -> HttpResponse:
    """Leave a review for a completed reservation (FR-21)."""
    reservation = get_object_or_404(Reservation.objects.with_related(), pk=reservation_id)
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_review(
                cast("User", request.user),
                reservation,
                form.cleaned_data["rating"],
                form.cleaned_data["comment"],
            )
        except DomainError as exc:
            messages.error(request, exc.message)
            return redirect("reservations:my")
        messages.success(request, "Sharhingiz saqlandi.")
        return redirect("cafes:detail", slug=reservation.table.zone.cafe.slug)
    return render(request, "reviews/form.html", {"form": form, "reservation": reservation})
