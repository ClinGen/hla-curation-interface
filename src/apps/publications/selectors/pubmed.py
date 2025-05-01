"""Provide selectors for PubMed publications."""

from django.db.models import Q, QuerySet

from apps.publications.models.pubmed import PubMedArticle
from base.selectors import EntitySelector


class PubMedArticleSelector(EntitySelector):
    """Get a specific PubMed publication or get a list of all PubMed publications."""

    def get(self, human_readable_id: str) -> PubMedArticle | None:
        """Return a specific PubMed publication.

        Args:
             human_readable_id: The PubMed ID of the publication.

        Returns:
            The PubMed article object or `None` if the PubMed ID is not found.
        """
        return PubMedArticle.objects.filter(pubmed_id=human_readable_id).first()

    def list(self, query: str | None = None) -> QuerySet[PubMedArticle] | None:
        """Return a list of all PubMed publications, optionally filtered.

        Args:
             query: The string to filter the PubMed articles by.

        Returns:
            The PubMed articles matching the query.
        """
        if query is None:
            return PubMedArticle.objects.all()
        return PubMedArticle.objects.filter(
            Q(pubmed_id__icontains=query) | Q(title__icontains=query)
        )
