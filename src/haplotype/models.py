"""Houses database models for the haplotype app."""

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele

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


class Haplotype(models.Model):
    """Contains information about a haplotype that has been added to the HCI."""

    alleles = models.ManyToManyField(
        Allele,
        blank=False,
        db_table="haplotype_allele_map",
        related_name="haplotypes",
        help_text="The constituent alleles of the haplotype.",
    )
    name = models.CharField(
        blank=False,
        default="",
        max_length=240,  # Should be plenty of characters.
        unique=True,
        verbose_name="Name",
        help_text=(
            "The name of the HLA haplotype, e.g., DRB1*15:01~DQB1*06:02. "
            "(The 'HLA-' part should be omitted.)"
        ),
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
        return self.name

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific haplotype."""
        return reverse("haplotype-detail", kwargs={"pk": self.pk})
