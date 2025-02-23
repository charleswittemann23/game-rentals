from django.urls import path

from . import views
from .views import dashboard
from .views import wishlist

app_name = "home"
urlpatterns = [
    path("", views.index, name="index"),
    path('dashboard/', dashboard, name='dashboard'),
    path("wishlist/", wishlist, name="wishlist"),
]