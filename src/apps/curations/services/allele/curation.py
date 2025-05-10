"""Provides services for creating and managing allele curations.

This module is meant to handle create and update logic.
"""

from apps.curations.models.allele.curation import AlleleCuration
from apps.diseases.models.mondo import Mondo
from apps.markers.models.allele import Allele
from apps.users.models.curator import Curator


class AlleleCurationServiceError(Exception):
    """Provides methods for creating and updating allele curations."""


class AlleleCurationService:
    """Create or update a PubMed article."""

    @staticmethod
    def create(disease: Mondo, allele: Allele, curator: Curator) -> AlleleCuration:
        """Creates a new allele curation linking a specific disease and allele.

        This method takes a `Mondo` disease object and an `Allele` object and
        creates a new `AlleleCuration` instance in the database, associating
        the given disease with the given allele.

        Args:
            disease: The `Mondo` disease object to associate with the allele.
            allele: The `Allele` object to associate with the disease.
            curator: The curator who created the curation.

        Returns:
            The newly created `AlleleCuration` object.
        """
        return AlleleCuration.objects.create(
            disease=disease, allele=allele, created_by=curator
        )

    # TODO(Liam): Implement the method below.  # noqa: FIX002, TD003
    @staticmethod
    def update() -> None:
        """Updates an existing allele curation.

        This method will likely take an `AlleleCuration` object (or its identifier)
        and allow for modifications to its associated data. The specific
        updatable fields and their behavior will be defined in the implementation.

        Returns:
            `None`.
        """
