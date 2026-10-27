"""URL routes for the reservations web views."""

from __future__ import annotations

from django.urls import path

from apps.reservations import views

app_name = "reservations"

urlpatterns = [
    path("search/", views.search_view, name="search"),
    path("book/", views.book_view, name="book"),
    path("my/", views.my_reservations_view, name="my"),
    path("schedule/", views.manager_schedule_view, name="schedule"),
    path("<int:pk>/confirm/", views.confirm_view, name="confirm"),
    path("<int:pk>/reject/", views.reject_view, name="reject"),
    path("<int:pk>/cancel/", views.cancel_view, name="cancel"),
    path("<int:pk>/complete/", views.complete_view, name="complete"),
    path("<int:pk>/no-show/", views.no_show_view, name="no_show"),
]
