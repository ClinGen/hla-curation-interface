"""Provide the configuration for the users app."""

from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    """Configure the users app."""

    name = "apps.users"
    verbose_name = "Affiliation and Curator Management"

    def ready(self) -> None:
        """Make sure admin models are registered."""
        import apps.users.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.users.models  # noqa: F401 (We don't care about unused imports in this context.)
