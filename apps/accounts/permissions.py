"""DRF permission classes for RBAC (FR-06, FR-07, §8.1)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.permissions import SAFE_METHODS, BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


def _has_role(request: Request, *roles: str) -> bool:
    user = request.user
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or getattr(user, "role", None) in roles)
    )


class IsAdmin(BasePermission):
    """Allow only administrators."""

    message = "Faqat administrator uchun ruxsat etilgan."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return _has_role(request, "ADMIN")


class IsManager(BasePermission):
    """Allow managers (and admins)."""

    message = "Faqat menejer uchun ruxsat etilgan."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return _has_role(request, "ADMIN", "MANAGER")


class IsCustomer(BasePermission):
    """Allow only customers.

    Unlike the admin/manager roles, this does not grant superusers an implicit
    pass: a customer-only endpoint must be reached as an actual CUSTOMER.
    """

    message = "Faqat mijoz uchun ruxsat etilgan."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "CUSTOMER")


class IsManagerOfCafe(BasePermission):
    """Allow the manager that owns the object's cafe (or an admin).

    Reads are allowed for any authenticated user; writes require ownership. The
    related object must expose a ``cafe`` attribute (directly or via a property).
    """

    message = "Ushbu kafeni boshqarishga ruxsatingiz yo'q."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return _has_role(request, "ADMIN", "MANAGER")

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or getattr(user, "role", None) == "ADMIN":
            return True
        # ``obj`` may be a Cafe (has ``manager``) or a related object (has ``cafe``).
        cafe = obj if hasattr(obj, "manager") else getattr(obj, "cafe", None)
        manager_id = getattr(getattr(cafe, "manager", None), "pk", None)
        return manager_id == user.pk


class IsOwnerOrReadOnly(BasePermission):
    """Allow read for everyone, write only for the object's owner.

    The object must expose one of ``customer``, ``author`` or ``user``.
    """

    message = "Ushbu obyektni faqat egasi o'zgartira oladi."

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        for attr in ("customer", "author", "user"):
            owner = getattr(obj, attr, None)
            if owner is not None:
                return getattr(owner, "pk", None) == user.pk
        return False
