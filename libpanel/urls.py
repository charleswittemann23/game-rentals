from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="libpanel"),
    path("requests/", views.requests, name="requests"),
    path("users/", views.users, name="users"),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
]