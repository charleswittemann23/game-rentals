from django.urls import path

from . import views

app_name = 'libpanel'

urlpatterns = [
    path("", views.index, name="index"),
    path("game_requests/", views.game_requests, name="game_requests"),
    path("collection_requests/", views.collection_requests, name="collection_requests"),
    path("users/", views.users, name="users"),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('approve_borrow/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('reject_borrow/<int:request_id>/', views.reject_borrow_request, name='reject_borrow_request'),
]