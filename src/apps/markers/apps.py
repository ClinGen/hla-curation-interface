"""Provide the configuration for the markers app."""

from django.apps import AppConfig


class MarkersAppConfig(AppConfig):
    """Configure the markers app."""

    name = "apps.markers"
    verbose_name = "Alleles and Haplotypes Management"

    def ready(self) -> None:
        """Make sure admin models are registered."""
        import apps.markers.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.markers.models  # noqa: F401 (We don't care about unused imports in this context.)
