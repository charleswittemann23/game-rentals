from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="catalog"),
    path('add_game/', views.add_game, name='add_game'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:pk>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:pk>/delete/', views.delete_collection, name='delete_collection'),
]