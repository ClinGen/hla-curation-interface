"""Provide the configuration for the diseases app."""

from django.apps import AppConfig


class DiseasesAppConfig(AppConfig):
    """Configure the diseases app."""

    name = "apps.diseases"
    verbose_name = "Diseases Management"

    def ready(self) -> None:
        """Make sure admin models are registered."""
        import apps.diseases.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.diseases.models  # noqa: F401 (We don't care about unused imports in this context.)
