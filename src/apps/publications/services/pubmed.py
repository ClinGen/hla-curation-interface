"""Provide services for PubMed articles."""

from apps.publications.clients.pubmed import PubMedArticleClient
from apps.publications.models import PubMedArticle
from base.services import EntityService


class PubMedArticleServiceError(Exception):
    """Raise when a PubMed service encounters an error."""


class PubMedArticleService(EntityService):
    """Create or update a PubMed article."""

    def __init__(self, client: PubMedArticleClient) -> None:
        """Set the PubMed article client."""
        self.client = client

    def create(self, pubmed_id: str) -> PubMedArticle:
        """Create a PubMed article.

        Args:
            pubmed_id: The PubMed ID of the article.

        Returns:
            The newly created PubMed article.
        """
        return PubMedArticle.objects.create(
            pubmed_id=pubmed_id, title=self.client.title
        )

    def update(self, pubmed_id: str, title: str) -> PubMedArticle:
        """Update a PubMed article.

        Args:
             pubmed_id: The PubMed ID of the article.
             title: The PubMed article title we want to update.

        Raises:
            PubMedArticleServiceError: When the PubMed article to update does not exist.

        Returns:
            The updated PubMed article.
        """
        try:
            article = PubMedArticle.objects.get(pubmed_id=pubmed_id)
            article.title = title
            article.save()
        except PubMedArticle.DoesNotExist as exc:
            error_message = f"The PubMed article with ID {pubmed_id} does not exist"
            raise PubMedArticleServiceError(error_message) from exc
        return article
