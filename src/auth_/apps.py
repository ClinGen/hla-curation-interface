"""Provides the configuration for the auth_ app."""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """Configures the auth_ app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_"
