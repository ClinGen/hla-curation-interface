"""Provide services for PubMed articles."""

from apps.curations.models.allele import AlleleCuration
from apps.diseases.models.mondo import Mondo
from apps.markers.models.allele import Allele


class AlleleCurationServiceError(Exception):
    """Raise when the `AlleleCuration` service encounters an error."""


class AlleleCurationService:
    """Create or update a PubMed article."""

    @staticmethod
    def create(
        disease: Mondo,
        allele: Allele,
    ) -> AlleleCuration:
        """Create a new curation.

        Args:
            disease: The disease for the curation.
            allele: The allele for the curation.

        Returns:
            The newly created curation.
        """
        return AlleleCuration.objects.create(disease=disease, allele=allele)

    # TODO(Liam): Implement the method below.  # noqa: FIX002, TD003
    @staticmethod
    def update() -> None:
        """Implement the method below."""
