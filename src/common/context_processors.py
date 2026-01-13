"""Houses context processors used throughout the app."""

from django.conf import settings


def git_sha(request) -> dict:  # noqa: ANN001 (Required to have the param.)
    """Returns the shortened Git SHA."""
    return {"GIT_SHA": settings.GIT_SHA}
