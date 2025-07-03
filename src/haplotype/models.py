"""Houses database models for the haplotype app."""

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele


class Haplotype(models.Model):
    """Contains information about a haplotype that has been added to the HCI."""

    car_id = models.CharField(
        blank=True,
        max_length=28,  # A CAR allele ID is of the form XAHLA718827727. 14 characters.
        null=True,
        unique=True,
        verbose_name="CAR ID",
        help_text="ClinGen Allele Registry ID, e.g., XAHLA718827727.",
    )
    alleles = models.ManyToManyField(
        Allele,
        db_table="haplotype_allele_map",
        related_name="haplotypes",
        help_text="The constituent alleles of the haplotype.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="haplotypes_added",
        verbose_name="Added By",
        help_text="The user who added the haplotype.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the haplotype was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "haplotype"
        verbose_name = "Haplotype"
        verbose_name_plural = "Haplotypes"

    def __str__(self) -> str:
        """Returns a string representation of a specific haplotype."""
        return f"Haplotype #{self.pk}"

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific haplotype."""
        return reverse("haplotype-detail", kwargs={"pk": self.pk})
