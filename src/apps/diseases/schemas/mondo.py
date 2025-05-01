"""Define schemas for the Mondo Disease Ontology API."""

from pydantic import BaseModel, ConfigDict


class TermsSchema(BaseModel):
    """Represent the response from the Mondo API's terms endpoint."""

    # There are many fields in the response. We only care about a small subset of the
    # fields.
    model_config = ConfigDict(extra="allow")
    label: str
