from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="libpanel"),
    path("requests/", views.index, name="requests"),
    path("users/", views.index, name="users")
]