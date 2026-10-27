"""URL routes for the cafes app."""

from __future__ import annotations

from django.urls import path

from apps.cafes import views

app_name = "cafes"

urlpatterns = [
    path("", views.cafe_list, name="list"),
    path("new/", views.cafe_create, name="create"),
    path("<slug:slug>/", views.cafe_detail, name="detail"),
    path("<slug:slug>/zones/new/", views.zone_create, name="zone_create"),
]
