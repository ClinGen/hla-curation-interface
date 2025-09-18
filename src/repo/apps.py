"""Provides the configuration for the repo app."""

from django.apps import AppConfig


class RepoConfig(AppConfig):
    """Configures the repo app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "repo"
