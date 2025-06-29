"""Houses database models for the publication app."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse


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


class Publication(models.Model):
    """Contains information about a publication that has been added to the HCI."""

    publication_type = models.CharField(
        blank=False,
        choices=PUBLICATION_TYPE_CHOICES,
        default=PublicationTypes.PUBMED,
        max_length=3,
        verbose_name="Publication Type",
        help_text=(
            f"One of: '{PublicationTypes.PUBMED}' (PubMed), "
            f"'{PublicationTypes.BIORXIV}' (bioRxiv), or "
            f"'{PublicationTypes.MEDRXIV}' (medRxiv)."
        ),
    )
    pubmed_id = models.CharField(
        blank=True,
        null=True,
        max_length=16,  # Most (all?) PubMed IDs are 8 characters long.
        unique=True,
        verbose_name="PubMed ID",
        help_text="The PubMed ID for the publication, e.g., 11910336.",
    )
    doi = models.CharField(
        blank=True,
        null=True,
        max_length=128,
        unique=True,
        verbose_name="Digital Object Identifier (DOI)",
        help_text="The DOI for the publication, e.g., 10.1000/182.",
    )
    title = models.CharField(
        blank=True,
        default="",
        max_length=256,
        verbose_name="Title",
        help_text="The title of the publication.",
    )
    author = models.CharField(
        blank=True,
        default="",
        max_length=16,
        verbose_name="Author",
        help_text="The surname of the primary author of the publication.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="publications_added",
        verbose_name="Added By",
        help_text="The user who added the publication.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the publication was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "publication"
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self) -> str:
        """Returns a string representation of the publication."""
        return f"{self.publication_type}/{self.doi}"

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific publication."""
        return reverse("publication-detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        """Makes sure PubMed articles have PubMed IDs.

        Raises:
            ValidationError: When the publication is a PubMed article and a PubMed ID
                             wasn't supplied.
        """
        super().clean()
        if self.publication_type == PublicationTypes.PUBMED and not self.pubmed_id:
            raise ValidationError(
                {"pubmed_id": "The PubMed ID is required for PubMed articles."}
            )
        if self.publication_type == PublicationTypes.BIORXIV and not self.doi:
            raise ValidationError({"doi": "The DOI is required for bioRxiv papers."})
        if self.publication_type == PublicationTypes.MEDRXIV and not self.doi:
            raise ValidationError({"doi": "The DOI is required for medRxiv papers."})
