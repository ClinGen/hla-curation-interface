"""Houses validation code for the models module of the publication app."""

from django.core.exceptions import ValidationError

from publication.constants.models import PublicationTypes


def validate_publication_type_pubmed(publication) -> None:
    """Makes sure we get a PubMed ID if the publication type is set to PubMed.

    Raises:
        ValidationError: If the PubMed ID for the PubMed publication isn't provided.
    """
    if (
        publication.publication_type == PublicationTypes.PUBMED
        and not publication.pubmed_id
    ):
        raise ValidationError(
            {"pubmed_id": "The PubMed ID is required for PubMed articles."}
        )


def validate_publication_type_biorxiv(publication) -> None:
    """Makes sure we get a DOI if the publication type is set to bioRxiv.

    Raises:
        ValidationError: If the DOI for the bioRxiv publication isn't provided.
    """
    if publication.publication_type == PublicationTypes.BIORXIV and not publication.doi:
        raise ValidationError({"doi": "The DOI is required for bioRxiv papers."})


def validate_publication_type_medrxiv(publication) -> None:
    """Makes sure we get a DOI if the publication type is set to medRxiv.

    Raises:
        ValidationError: If the DOI for the medRxiv publication isn't provided.
    """
    if publication.publication_type == PublicationTypes.MEDRXIV and not publication.doi:
        raise ValidationError({"doi": "The DOI is required for medRxiv papers."})
