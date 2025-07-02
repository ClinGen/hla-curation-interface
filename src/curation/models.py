"""Houses database models for the curation app."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from allele.models import Allele


class CurationTypes:
    """Defines the curation type codes."""

    ALLELE = "ALL"
    HAPLOTYPE = "HAP"


CURATION_TYPE_CHOICES = {
    CurationTypes.ALLELE: "Allele",
    CurationTypes.HAPLOTYPE: "Haplotype",
}


class Curation(models.Model):
    """Contains top-level information about a curation."""

    curation_type = models.CharField(
        blank=False,
        choices=CURATION_TYPE_CHOICES,
        default=CurationTypes.ALLELE,
        max_length=3,
        verbose_name="Curation Type",
        help_text=(
            f"Either '{CurationTypes.ALLELE}' (allele) or "
            f"'{CurationTypes.HAPLOTYPE}' (haplotype)."
        ),
    )
    allele = models.ForeignKey(
        Allele,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="Select the allele for this curation.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="curations_added",
        verbose_name="Added By",
        help_text="The user who added the curation.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the curation was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "curation"
        verbose_name = "Curation"
        verbose_name_plural = "Curations"

    def __str__(self) -> str:
        """Returns a string representation of the curation."""
        return f"Curation #{self.pk} ({self.curation_type})"

    def clean(self) -> None:
        """Makes sure an allele curation has an allele.

        Raises:
            ValidationError: When the curation type is allele but the allele for the
                             curation is not provided.
        """
        super().clean()
        if self.curation_type == CurationTypes.ALLELE and not self.allele:
            raise ValidationError(
                {"allele": "An allele is required for allele curations."}
            )
