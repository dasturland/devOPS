"""URL routes for the dashboard app."""

from __future__ import annotations

from django.urls import path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("admin/", views.admin_dashboard, name="admin"),
]
