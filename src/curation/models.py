"""Houses database models for the curation app."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele
from haplotype.models import Haplotype


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
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="Select the allele for this curation.",
    )
    haplotype = models.ForeignKey(
        Haplotype,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="Select the haplotype for this curation.",
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

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific publication."""
        return reverse("curation-detail", kwargs={"pk": self.pk})

    def clean(self) -> None:
        """Makes sure the curation has an allele or haplotype.

        Also makes sure that haplotype information isn't added to an allele curation
        and vice versa.

        Raises:
            ValidationError: When the curation type is allele but the allele for the
                             curation is not provided. Same for haplotype.
        """
        super().clean()
        if self.curation_type == CurationTypes.ALLELE and not self.allele:
            raise ValidationError(
                {"allele": "An allele is required for an allele curation."}
            )
        if self.curation_type == CurationTypes.HAPLOTYPE and not self.haplotype:
            raise ValidationError(
                {"haplotype": "A haplotype is required for a haplotype curation."}
            )
        if self.curation_type == CurationTypes.ALLELE and self.haplotype:
            self.haplotype = None
        if self.curation_type == CurationTypes.HAPLOTYPE and self.allele:
            self.allele = None
