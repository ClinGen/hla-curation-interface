"""Configures the `curations` application.

The `curations` application manages the creation, display, and modification of
allele-disease and haplotype-disease curations.
"""

from django.apps import AppConfig


class CurationsAppConfig(AppConfig):
    """Configures the `curations` app."""

    name = "apps.curations"
    verbose_name = "Curations Management"

    def ready(self) -> None:
        """Performs initialization tasks when the `curations` app is ready.

        Specifically, this method imports the `admin` and `models` modules
        within the `curations` app to ensure that the associated models
        are registered with the Django admin site and that our models are
        picked up.
        """
        import apps.curations.admin  # noqa: F401 (We don't care about unused imports in this context.)
        import apps.curations.models  # noqa: F401 (We don't care about unused imports in this context.)
