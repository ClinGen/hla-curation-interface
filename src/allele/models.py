"""Houses database models for the allele app."""

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

# Genes on chromosome 6 ordered by location in ascending order.
GENE_LIST = [
    "HFE",
    "F",
    "V",
    "P",
    "G",
    "H",
    "T",
    "K",
    "U",
    "A",
    "W",
    "Y",
    "R",
    "J",
    "L",
    "N",
    "E",
    "C",
    "B",
    "S",
    "MICA",
    "MICB",
    "DRA",
    "DRB9",
    "DRB8",
    "DRB7",
    "DRB6",
    "DRB5",
    "DRB4",
    "DRB3",
    "DRB2",
    "DRB1",
    "DQA1",
    "DQB1",
    "DQB3",
    "DQA2",
    "DQB2",
    "DOB",
    "TAP2",
    "TAP1",
    "Z",
    "DMB",
    "DMA",
    "DOA",
    "DPA1",
    "DPB1",
    "DPA2",
    "DPB2",
]


class Allele(models.Model):
    """Contains information about an allele that has been added to the HCI."""

    name = models.CharField(
        blank=False,
        default="",
        max_length=60,
        unique=True,
        verbose_name="Name",
        help_text=(
            "The name of the HLA allele, e.g., DRB3*03:01. "
            "(The 'HLA-' part can be omitted.)"
        ),
    )
    car_id = models.CharField(
        blank=True,
        max_length=28,  # A CAR allele ID is of the form XAHLA718827727. 14 characters.
        null=True,
        unique=True,
        verbose_name="CAR ID",
        help_text="ClinGen Allele Registry ID, e.g., XAHLA718827727.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="alleles_added",
        verbose_name="Added By",
        help_text="The user who added the allele.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the allele was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "allele"
        verbose_name = "Allele"
        verbose_name_plural = "Alleles"

    def __str__(self) -> str:
        """Returns a string representation of the allele."""
        return f"{self.car_id}"

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific allele."""
        return reverse("allele-detail", kwargs={"pk": self.pk})
