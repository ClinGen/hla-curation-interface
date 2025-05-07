"""Provides selectors for retrieving allele curations.

This module is meant to handle read logic.
"""

from django.db.models import Q, QuerySet

from apps.curations.models.allele import AlleleCuration
from base.selectors import EntitySelector


class AlleleCurationSelector(EntitySelector):
    """Provides methods for retrieving allele curations."""

    def get(self, human_readable_id: str) -> AlleleCuration | None:
        """Retrieves a specific allele curation based on the provided human-readable ID.

        Args:
             human_readable_id: The unique, user-friendly identifier assigned to the
                allele curation.

        Returns:
            The `AlleleCuration` object matching the provided `human_readable_id`,
            or `None` if no such curation exists.
        """
        return AlleleCuration.objects.filter(curation_id=human_readable_id).first()

    def list(
        self, query: str | None = None
    ) -> QuerySet[AlleleCuration] | QuerySet[None]:
        """Retrieves a list of allele curations, optionally filtered based on the query.

        Args:
            query: An optional string to filter the allele curations. If provided, the
                   returned list will only contain curations whose `curation_id`
                   contains the query string (case-insensitive). If `None`, all allele
                   curations are returned.

        Returns:
            A `QuerySet` containing the `AlleleCuration` objects that match the optional
            query. If no query is provided, all `AlleleCuration` objects are returned
            in the `QuerySet`. If no matching curations are found with a query, an empty
            `QuerySet` will be returned.
        """
        if query is None:
            return AlleleCuration.objects.all()
        return AlleleCuration.objects.filter(Q(curation_id__icontains=query))
