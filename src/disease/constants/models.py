"""Houses constants used in the models module of the curation app."""


class DiseaseTypes:
    """Defines the disease ontology type codes."""

    MONDO = "MON"


DISEASE_TYPE_CHOICES = {
    DiseaseTypes.MONDO: "Mondo",
}
