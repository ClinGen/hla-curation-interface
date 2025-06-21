"""Provides the configuration for the publications app."""

from django.apps import AppConfig


class PublicationsConfig(AppConfig):
    """Configures the publications app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "publications"
