"""
backend URL Configuration
--- 
Handles admin site for us, so that we can view data in PostGreSQL easily.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from .views import frontend

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirecting to endpoints that communicates with frontend.
    path("", include("recommender.urls")),
    path("", frontend),
    re_path(r'.*', frontend)
]

# for uploaded files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# for static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
