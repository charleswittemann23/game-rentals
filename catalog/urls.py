from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path("", views.index, name="index"),
    path('add_game/', views.add_game, name='add_game')
]
