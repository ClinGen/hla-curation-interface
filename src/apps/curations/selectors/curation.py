"""Provide selectors for curations."""

from django.db.models import Q, QuerySet

from apps.curations.models.allele import AlleleCuration
from base.selectors import EntitySelector


class AlleleCurationSelector(EntitySelector):
    """Get a specific curation or get a list of curations."""

    def get(self, human_readable_id: str) -> AlleleCuration | None:
        """Return a specific curation.

        Args:
             human_readable_id: The curation ID.

        Returns:
            The curation object or `None` if the curation ID is not found.
        """
        return AlleleCuration.objects.filter(curation_id=human_readable_id).first()

    def list(self, query: str | None = None) -> QuerySet[AlleleCuration] | None:
        """Return a list of all curations, optionally filtered.

        Args:
             query: The string to filter the curations by.

        Returns:
            The curations matching the query.
        """
        if query is None:
            return AlleleCuration.objects.all()
        return AlleleCuration.objects.filter(Q(curation_id__icontains=query))
