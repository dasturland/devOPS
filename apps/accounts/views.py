"""Web views for authentication and profile management (FR-02..FR-05)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import (
    ChangePasswordForm,
    LoginForm,
    PasswordResetRequestForm,
    ProfileForm,
    RegisterForm,
    SetNewPasswordForm,
)
from apps.accounts.services import (
    change_password,
    confirm_password_reset,
    issue_password_reset,
    register_customer,
)
from apps.core.exceptions import ValidationError

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from apps.accounts.models import User


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    """Register a new customer and log them in (FR-01)."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = register_customer(form.cleaned_data)
        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz.")
        return redirect("dashboard:home")
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """Authenticate a user by email/password (FR-02)."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        messages.success(request, "Tizimga muvaffaqiyatli kirdingiz.")
        return redirect("dashboard:home")
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """Log the current user out (FR-03)."""
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("core:home")


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request: HttpRequest) -> HttpResponse:
    """View and edit the authenticated user's profile (FR-04)."""
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil yangilandi.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request: HttpRequest) -> HttpResponse:
    """Change the authenticated user's password (FR-04)."""
    form = ChangePasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            change_password(
                cast("User", request.user),
                form.cleaned_data["old_password"],
                form.cleaned_data["new_password"],
            )
        except ValidationError as exc:
            form.add_error("old_password", exc.message)
        else:
            messages.success(request, "Parol o'zgartirildi. Qaytadan kiring.")
            logout(request)
            return redirect("accounts:login")
    return render(request, "accounts/change_password.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request: HttpRequest) -> HttpResponse:
    """Request a password reset email (FR-05)."""
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        issue_password_reset(form.cleaned_data["email"])
        messages.info(
            request,
            "Agar email ro'yxatdan o'tgan bo'lsa, tiklash havolasi yuborildi.",
        )
        return redirect("accounts:login")
    return render(request, "accounts/password_reset.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    """Set a new password via the reset link (FR-05)."""
    form = SetNewPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            confirm_password_reset(uidb64, token, form.cleaned_data["new_password"])
        except ValidationError as exc:
            messages.error(request, exc.message)
            return redirect("accounts:password_reset")
        messages.success(request, "Parol yangilandi. Endi tizimga kiring.")
        return redirect("accounts:login")
    return render(request, "accounts/password_reset_confirm.html", {"form": form})
