"""Provides the configuration for the publication app."""

from django.apps import AppConfig


class PublicationConfig(AppConfig):
    """Configures the publication app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "publication"
