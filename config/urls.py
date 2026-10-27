"""Root URL configuration (§10.1).

Wires up the admin, the health-check endpoint, the versioned REST API, the
Django-template web application and the custom 403/404/500 handlers.
"""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", core_views.health_check, name="health"),
    path("api/", include("apps.api.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cafes/", include("apps.cafes.urls")),
    path("tables/", include("apps.tables.urls")),
    path("reservations/", include("apps.reservations.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (FR-29). These must resolve to a dotted callable path.
handler403 = "apps.core.views.handler403"
handler404 = "apps.core.views.handler404"
handler500 = "apps.core.views.handler500"
