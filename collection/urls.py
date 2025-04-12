from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="collection"),
    path('create/', views.create_collection, name='create_collection'),
    path('<int:pk>/', views.view_collection, name='view_collection'),
    path('<int:pk>/edit/', views.edit_collection, name='edit_collection'),
    path('<int:pk>/delete/', views.delete_collection, name='delete_collection'),
]