"""Provides the configuration for the datatable app."""

from django.apps import AppConfig


class DatatableConfig(AppConfig):
    """Configures the datatable app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "datatable"
