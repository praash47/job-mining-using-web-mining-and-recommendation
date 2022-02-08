"""
Django application configuration for django checkers app.
"""
from django.apps import AppConfig


class CheckersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checkers"
