"""
backend URL Configuration
--- 
Handles admin site for us, so that we can view data in PostGreSQL easily.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Redirecting to endpoints that communicates with frontend.
    path("", include("recommender.urls")),
]
