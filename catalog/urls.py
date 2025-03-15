from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="catalog"),
    path('add/', views.add_game, name='add_game')
]