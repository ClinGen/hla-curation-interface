"""Provide read-only for `Curator` objects."""

import logging

from apps.users.models import Curator

logger = logging.getLogger(__name__)


def get_curator(username: str) -> Curator | None:
    """Return `Curator` object for the given username."""
    curator = None
    try:
        logger.info(f"Getting Curator object for {username}")
        curator = Curator.objects.get(user__username=username)
    except Curator.DoesNotExist:
        logger.warning(f"Could not find Curator object for {username}")
    return curator
