from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="collection"),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collection/<int:pk>/', views.view_collection, name='view_collection'),
    path('collections/<int:pk>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:pk>/delete/', views.delete_collection, name='delete_collection'),
]