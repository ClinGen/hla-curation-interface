"""Provide selectors for curations."""

from django.db.models import Q, QuerySet

from apps.curations.models.curation import Curation
from base.selectors import EntitySelector


class CurationSelector(EntitySelector):
    """Get a specific curation or get a list of curations."""

    def get(self, human_readable_id: str) -> Curation | None:
        """Return a specific curation.

        Args:
             human_readable_id: The curation ID.

        Returns:
            The curation object or `None` if the curation ID is not found.
        """
        return Curation.objects.filter(curation_id=human_readable_id).first()

    def list(self, query: str | None = None) -> QuerySet[Curation] | None:
        """Return a list of all curations, optionally filtered.

        Args:
             query: The string to filter the curations by.

        Returns:
            The curations matching the query.
        """
        if query is None:
            return Curation.objects.all()
        return Curation.objects.filter(Q(curation_id__icontains=query))
