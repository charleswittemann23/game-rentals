from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "home"
urlpatterns = [
                  path("", views.index, name="index"),
                  path("wishlist/", views.wishlist, name="wishlist"),
                  path("update_user/", views.update_user, name='update_user')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
