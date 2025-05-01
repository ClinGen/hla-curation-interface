"""Provide a client for getting data from the Mondo Disease Ontology API."""

from urllib.parse import quote

from pydantic import ValidationError

from apps.diseases.schemas.mondo import TermsSchema
from base.clients import EntityClient, EntityClientError
from constants import MondoConstants


class MondoClientError(Exception):
    """Raise when a Mondo client encounters an error."""


class MondoClient(EntityClient):
    """Get data from the Mondo Disease Ontology API."""

    def __init__(self, mondo_id: str, schema: type[TermsSchema] = TermsSchema) -> None:
        """Set up the Mondo client."""
        super().__init__(base_url=MondoConstants.API_URL)
        self.mondo_id = mondo_id
        self.schema = schema
        self.label = None

    def fetch(self) -> None:
        """Fetch data from the Mondo API and populate the members.

        Raises:
             MondoClientError: If the request fails, or we can't extract the data from
                 the response.
        """
        try:
            double_quoted_iri = quote(quote(MondoConstants.IRI))
            endpoint = f"{self.base_url}/{double_quoted_iri}{self.mondo_id}"
            json_data = self.get_json(endpoint)
            valid_data = self.schema.model_validate(json_data)
            self.label = valid_data.label
        except ValidationError as exc:
            error_message = f"Error validating data for {self.mondo_id}: {exc}"
            raise MondoClientError(error_message) from exc
        except EntityClientError as exc:
            error_message = f"Error fetching Mondo data for {self.mondo_id}: {exc}"
            raise MondoClientError(error_message) from exc
