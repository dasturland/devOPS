"""URL routes for the tables app."""

from __future__ import annotations

from django.urls import path

from apps.tables import views

app_name = "tables"

urlpatterns = [
    path("zone/<int:zone_id>/", views.table_list, name="list"),
    path("zone/<int:zone_id>/new/", views.table_create, name="create"),
]
