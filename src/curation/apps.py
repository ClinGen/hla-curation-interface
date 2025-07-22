"""Provides the configuration for the curation app."""

from django.apps import AppConfig


class CurationConfig(AppConfig):
    """Configures the curation app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "curation"
