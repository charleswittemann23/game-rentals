from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="libpanel"),
    path("game_requests/", views.game_requests, name="game_requests"),
    path("collection_requests/", views.collection_requests, name="collection_requests"),
    path("users/", views.users, name="users"),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
]