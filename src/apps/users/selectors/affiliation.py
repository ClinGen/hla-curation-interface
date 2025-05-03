"""Provide read-only for `Affiliation` objects."""

import logging

from apps.users.models import Affiliation

logger = logging.getLogger(__name__)


def get_affiliation(affiliation_id: str) -> Affiliation | None:
    """Return `Affiliation` object for the given ID."""
    affiliation = None
    try:
        logger.info(f"Getting Affiliation object for {affiliation_id}")
        affiliation = Affiliation.objects.get(affiliation_id=affiliation_id)
    except Affiliation.DoesNotExist:
        logger.warning(f"Could not find Affiliation object for {affiliation_id}")
    return affiliation
