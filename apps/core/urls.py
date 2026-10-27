"""URL routes for the core app."""

from __future__ import annotations

from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
]
