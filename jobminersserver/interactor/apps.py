"""
Application Configuration of interactor being a django application
"""

from django.apps import AppConfig


class InteractorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "interactor"
