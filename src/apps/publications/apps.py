"""Provide the configuration for the publications app."""

from django.apps import AppConfig


class PublicationsAppConfig(AppConfig):
    """Configure the publications app."""

    name = "apps.publications"
    verbose_name = "Publications Management"

    def ready(self) -> None:
        """Make sure admin models are registered."""
        import apps.publications.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.publications.models  # noqa: F401 (We don't care about unused imports in this context.)
