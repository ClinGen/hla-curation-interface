"""Houses constants used in the models module of the publication app."""


class PublicationTypes:
    """Defines the publication type codes."""

    PUBMED = "PUB"
    BIORXIV = "BIO"
    MEDRXIV = "MED"


PUBLICATION_TYPE_CHOICES = {
    PublicationTypes.PUBMED: "PubMed Article",
    PublicationTypes.BIORXIV: "bioRxiv Paper",
    PublicationTypes.MEDRXIV: "medRxiv Paper",
}
