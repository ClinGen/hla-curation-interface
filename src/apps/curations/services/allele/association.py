"""Provides services for creating and managing allele associations.

This module is meant to handle create and update logic.
"""

from apps.curations.models.allele.association import PubMedAlleleAssociation
from apps.curations.selectors.allele.curation import AlleleCurationSelector
from base.services import EntityService


class AlleleAssociationServiceError(Exception):
    """Provides methods for creating and updating allele associations."""


class AlleleAssociationService(EntityService):
    """Create or update an allele association."""

    # TODO(Liam): Add biorxiv and medrxiv support.  # noqa: FIX002, TD003
    @staticmethod
    def create(
        curation_id: str,
        publication_type: str,
    ) -> PubMedAlleleAssociation | None:
        """Creates a new allele association based on the given publication type.

        Args:
            curation_id: The curation this association is linked to.
            publication_type: Either "pubmed", "biorxiv", or "medrxiv".

        Returns:
            The newly created allele association object or `None` if the choice of
            publication type wasn't valid.
        """
        if publication_type == "pubmed":
            curation_selector = AlleleCurationSelector()
            curation = curation_selector.get(curation_id)
            return PubMedAlleleAssociation.objects.create(curation=curation)
        return None

    # TODO(Liam): Implement the method below.  # noqa: FIX002, TD003
    @staticmethod
    def update() -> None:
        """Updates an existing allele association.

        Returns:
            `None`.
        """
