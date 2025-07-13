"""Houses database models for the disease app."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse


class DiseaseTypes:
    """Defines the disease ontology type codes."""

    MONDO = "MON"


DISEASE_TYPE_CHOICES = {
    DiseaseTypes.MONDO: "Mondo",
}


class Disease(models.Model):
    """Contains information about a disease that has been added to the HCI."""

    disease_type = models.CharField(
        blank=True,
        choices=DISEASE_TYPE_CHOICES,
        default=DiseaseTypes.MONDO,
        max_length=3,
        verbose_name="Disease Type",
        help_text=(
            "The disease ontology type. Only Mondo diseases are supported for now."
        ),
    )
    mondo_id = models.CharField(
        blank=False,
        default="",
        max_length=26,  # A Mondo ID is of the form MONDO:1234567. 13 characters.
        unique=True,
        verbose_name="Mondo ID",
        help_text="The Mondo Disease Ontology ID, e.g., MONDO:1234567.",
    )
    iri = models.CharField(
        blank=True,
        default="",
        max_length=88,  # A typical disease IRI is 44 characters long.
        verbose_name="Internationalized Resource Identifier (IRI)",
    )
    name = models.CharField(
        blank=True,
        default="",
        max_length=256,
        verbose_name="Name",
        help_text="The name of the disease.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="diseases_added",
        verbose_name="Added By",
        help_text="The user who added the disease.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the disease was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "disease"
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"

    def __str__(self) -> str:
        """Returns a string representation of the disease."""
        return self.name

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific disease."""
        return reverse("disease-detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        """Makes sure the disease is valid.

        Raises:
            ValidationError: If a field that is necessary isn't supplied or if data is
                             not properly formed.
        """
        super().clean()
        if self.disease_type == DiseaseTypes.MONDO and not self.mondo_id:
            raise ValidationError(
                {"mondo_id": "The Mondo ID is required for Mondo disease."}
            )
        if self.mondo_id and "MONDO:" not in self.mondo_id[:6]:
            raise ValidationError(
                {"mondo_id": "The prefix 'MONDO:' is required for Mondo IDs."}
            )
