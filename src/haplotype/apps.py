"""Provides the configuration for the haplotype app."""

from django.apps import AppConfig


class HaplotypeConfig(AppConfig):
    """Configures the haplotype app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "haplotype"
