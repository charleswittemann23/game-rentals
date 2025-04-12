from django.urls import path

from . import views

app_name = 'collection'

urlpatterns = [
    path("", views.index, name="index"),
    path('create/', views.create_collection, name='create_collection'),
    path('<int:pk>/', views.view_collection, name='view_collection'),
    path('edit/<int:pk>/', views.edit_collection, name='edit_collection'),
    path('delete/<int:pk>/', views.delete_collection, name='delete_collection'),
    path('request-access/<int:collection_id>/', views.request_access, name='request_access'),
    path('manage-access-requests/', views.manage_access_requests, name='manage_access_requests'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
]