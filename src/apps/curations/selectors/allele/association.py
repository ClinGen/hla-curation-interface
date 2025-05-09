"""Provides selectors for retrieving allele associations.

This module is meant to handle read logic.
"""

from django.db.models import Q, QuerySet

from apps.curations.models.allele.association import PubMedAlleleAssociation
from base.selectors import EntitySelector


class PubMedAlleleAssociationSelector(EntitySelector):
    """Provides methods for retrieving PubMed allele associations."""

    def get(self, human_readable_id: str) -> PubMedAlleleAssociation | None:
        """Retrieves a specific association based on the provided ID.

        Args:
             human_readable_id: The unique, user-friendly identifier assigned to the
                allele association.

        Returns:
            The `PubMedAlleleAssociation` object matching the provided
            `human_readable_id`, or `None` if no such curation exists.
        """
        return PubMedAlleleAssociation.objects.filter(
            association_id=human_readable_id
        ).first()

    def list(
        self, query: str | None = None
    ) -> QuerySet[PubMedAlleleAssociation] | None:
        """Retrieves a list of associations, optionally filtered based on the query.

        Args:
            query: An optional string to filter the allele associations. If provided,
                   the returned list will only contain curations whose `association_id`
                   contains the query string (case-insensitive). If `None`, all allele
                   associations are returned.

        Returns:
            A `QuerySet` containing the `PubMedAlleleAssociation` objects that match the
            optional query. If no query is provided, all `PubMedAlleleAssociation`
            objects are returned in the `QuerySet`. If no matching associations are
            found with a query, an empty `QuerySet` (which we type as `None`) will be
            returned.
        """
        if query is None:
            return PubMedAlleleAssociation.objects.all()
        return PubMedAlleleAssociation.objects.filter(
            Q(association_id__icontains=query)
        )
