"""Provides the configuration for the allele app."""

from django.apps import AppConfig


class AlleleConfig(AppConfig):
    """Configures the allele app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "allele"
