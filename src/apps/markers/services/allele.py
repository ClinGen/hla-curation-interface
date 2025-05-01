"""Provide services for HLA alleles."""

from apps.markers.clients.allele import AlleleClient
from apps.markers.models import Allele
from base.services import EntityService


class AlleleServiceError(Exception):
    """Raise when `AlleleService` encounters an error."""


class AlleleService(EntityService):
    """Create or update an allele."""

    def __init__(self, client: AlleleClient) -> None:
        """Set the allele client."""
        self.client = client

    def create(self, descriptor: str) -> Allele:
        """Create an HLA allele in the database.

        Args:
             descriptor: The HLA allele descriptor, e.g., 'A*01:01:01:119'.

        Returns:
            The newly created HLA allele object.
        """
        return Allele.objects.create(
            descriptor=descriptor,
            car_id=self.client.car_id,
            car_url=self.client.car_url,
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    def update(self, car_id: str) -> Allele:  # type: ignore
        """Update an HLA allele.

        Args:
            car_id: The ClinGen Allele Registry ID, e.g., CAHLA1449130330.

        Raises:
            AlleleServiceError: When the allele to update does not exist.

        Returns:
            The updated HLA allele.
        """
