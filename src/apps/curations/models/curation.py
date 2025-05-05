"""Provide a model for curations."""

from django.db import models

from apps.diseases.models import Mondo
from apps.markers.models import Allele
from constants import ModelsConstants


class Curation(models.Model):
    """A curation is the basic information about a classification."""

    CURATION_TYPES = [
        ("allele", "Allele"),
    ]
    curation_type: models.CharField = models.CharField(
        choices=CURATION_TYPES,
        default="allele",
        max_length=ModelsConstants.MAX_LENGTH_NAME,
        verbose_name="Curation Type",
        help_text="The type of curation, e.g., 'allele' or 'haplotype'.",
    )
    disease: models.ForeignKey = models.ForeignKey(Mondo, on_delete=models.CASCADE)
    allele: models.ForeignKey = models.ForeignKey(
        Allele, on_delete=models.CASCADE, null=True
    )
    status: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_NAME,
        verbose_name="Status",
        help_text="The status of the curation, e.g., 'new', 'in progress', 'done'.",
        default="new",
    )
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="Created At", auto_now_add=True
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="Updated At", auto_now=True
    )

    def __str__(self) -> str:
        """Return a string representation of the curation."""
        return f"{self.status} {self.curation_type} curation"
