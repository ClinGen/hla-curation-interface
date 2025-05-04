"""Define schemas for the Mondo Disease Ontology API."""

from pydantic import BaseModel, ConfigDict, Field


class Term(BaseModel):
    """Define the shape of the `terms` object.

    This is the "meat" of the Mondo API response.
    """

    # There are other fields, but we don't need them for now.
    model_config = ConfigDict(extra="allow")

    # These are the fields we care about.
    description: list[str]
    label: str


class Embedded(BaseModel):
    """Define the shape of the `_embedded` list."""

    terms: list[Term]


class MondoAPIResponse(BaseModel):
    """Define the Mondo API response schema."""

    model_config = ConfigDict(extra="allow")
    embedded: Embedded = Field(alias="_embedded")
