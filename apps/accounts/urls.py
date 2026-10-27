"""URL routes for the accounts app."""

from __future__ import annotations

from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("password/change/", views.change_password_view, name="change_password"),
    path("password/reset/", views.password_reset_request_view, name="password_reset"),
    path(
        "reset/<str:uidb64>/<str:token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
]
