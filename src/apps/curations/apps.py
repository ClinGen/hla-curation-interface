"""Provide the configuration for the curations app."""

from django.apps import AppConfig


class CurationsAppConfig(AppConfig):
    """Configure the curations app."""

    name = "apps.curations"
    verbose_name = "Curations Management"

    def ready(self) -> None:
        """Make sure admin models are registered."""
        import apps.curations.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.curations.models  # noqa: F401 (We don't care about unused imports in this context.)
