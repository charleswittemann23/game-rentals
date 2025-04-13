from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', RedirectView.as_view(url='/accounts/google/login/', permanent=False)),
    path('accounts/', include('allauth.urls')),

    path('', include('home.urls')),
    path("catalog/", include("catalog.urls")),
    path('collections/', include('collection.urls')),
    path("manage/", include("libpanel.urls", namespace="libpanel")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
