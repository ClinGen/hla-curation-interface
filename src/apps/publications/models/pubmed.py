"""Provide a model for PubMed publications."""

from django.db import models


class PubMedArticle(models.Model):
    """A PubMed article is a scientific paper published in PubMed."""

    pubmed_id: models.CharField = models.CharField(
        verbose_name="PubMed ID",
        help_text="A PubMed ID is a unique numeric ID associated with the article.",
    )
    title: models.CharField = models.CharField(verbose_name="Article Title")

    class Meta:
        """Define metadata options."""

        verbose_name = "PubMed Article"
        verbose_name_plural = "PubMed Articles"

    def __str__(self) -> str:
        """Return a string representation of the PubMed article."""
        return f"{self.title} ({self.pubmed_id})"
