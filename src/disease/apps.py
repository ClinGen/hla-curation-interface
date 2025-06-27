"""Provides the configuration for the disease app."""

from django.apps import AppConfig


class DiseasesConfig(AppConfig):
    """Configures the disease app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "disease"
