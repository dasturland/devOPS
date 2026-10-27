"""URL routes for the reviews app."""

from __future__ import annotations

from django.urls import path

from apps.reviews import views

app_name = "reviews"

urlpatterns = [
    path("reservation/<int:reservation_id>/", views.create_review_view, name="create"),
]
