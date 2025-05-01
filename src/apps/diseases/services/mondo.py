"""Provide services for Mondo diseases."""

from apps.diseases.clients.mondo import MondoClient
from apps.diseases.models.mondo import Mondo
from base.services import EntityService


class MondoServiceError(Exception):
    """Raise when a Mondo service encounters an error."""


class MondoService(EntityService):
    """Create or update a Mondo disease."""

    def __init__(self, client: MondoClient) -> None:
        """Set the Mondo client."""
        self.client = client

    def create(self, mondo_id: str) -> Mondo:
        """Create a Mondo disease.

        Args:
             mondo_id: The Mondo Disease Ontology ID, e.g., MONDO_0005052.

        Returns:
            The newly created Mondo disease.
        """
        return Mondo.objects.create(mondo_id=mondo_id, label=self.client.label)

    def update(self, mondo_id: str, label: str) -> Mondo:
        """Update a Mondo disease.

        Args:
             mondo_id: The Mondo Disease Ontology ID, e.g., MONDO_0005052.
             label: The Mondo disease label we want to update.

        Raises:
            MondoServiceError: When the Mondo disease to update does not exist.

        Returns:
            The updated Mondo disease.
        """
        try:
            disease = Mondo.objects.get(mondo_id=mondo_id)
            disease.label = label
            disease.save()
        except Mondo.DoesNotExist as exc:
            error_message = f"The Mondo disease with ID {mondo_id} does not exist"
            raise MondoServiceError(error_message) from exc
        return disease
