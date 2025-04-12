from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="catalog"),
    path('add_game/', views.add_game, name='add_game')
]
