"""Provide services for PubMed articles."""

from apps.curations.models.curation import Curation
from apps.diseases.models.mondo import Mondo
from apps.markers.models.allele import Allele
from apps.users.models.curator import Curator


class CurationServiceError(Exception):
    """Raise when the `Curation` service encounters an error."""


class CurationService:
    """Create or update a PubMed article."""

    @staticmethod
    def create(
        curation_type: str,
        disease: Mondo,
        allele: Allele,
        user: Curator,
    ) -> Curation:
        """Create a new curation.

        Args:
            curation_type: The type of curation, either 'allele' or 'haplotype'.
            disease: The disease for the curation.
            allele: The allele for the curation.
            user: The user who created the curation.

        Returns:
            The newly created curation.
        """
        return Curation.objects.create(
            curation_type=curation_type, disease=disease, allele=allele, created_by=user
        )

    # TODO(Liam): Implement the method below.  # noqa: FIX002, TD003
    @staticmethod
    def update() -> None:
        """Implement the method below."""
