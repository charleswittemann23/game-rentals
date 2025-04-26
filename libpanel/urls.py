from django.urls import path

from . import views

app_name = 'libpanel'

urlpatterns = [
    path("requests/", views.requests, name="requests"),
    path("users/", views.users, name="users"),
    path("loans/", views.loans, name="loans"),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('approve_borrow/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('reject_borrow/<int:request_id>/', views.reject_borrow_request, name='reject_borrow_request'),
    path('collection-request/<int:request_id>/approve/', views.approve_collection_access_request, name='approve_access_request'),
    path('collection-request/<int:request_id>/reject/', views.reject_access_request, name='reject_access_request'),
]