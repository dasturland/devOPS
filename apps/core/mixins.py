"""Reusable view mixins for role based access control (FR-06, FR-07)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

__all__ = [
    "LoginRequiredMixin",
    "RoleRequiredMixin",
    "AdminRequiredMixin",
    "ManagerRequiredMixin",
    "CustomerRequiredMixin",
]


class RoleRequiredMixin(AccessMixin):
    """Allow access only to authenticated users whose role is permitted.

    Subclasses set :attr:`allowed_roles`. Superusers always pass so the admin
    account can reach every page.
    """

    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        if not user.is_superuser and getattr(user, "role", None) not in self.allowed_roles:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


class AdminRequiredMixin(RoleRequiredMixin):
    """Restrict a view to administrators."""

    allowed_roles = ("ADMIN",)


class ManagerRequiredMixin(RoleRequiredMixin):
    """Restrict a view to cafe managers (and admins)."""

    allowed_roles = ("ADMIN", "MANAGER")


class CustomerRequiredMixin(RoleRequiredMixin):
    """Restrict a view to customers."""

    allowed_roles = ("CUSTOMER",)
