"""Houses database models for the haplotype app."""

from django.contrib.auth.models import User
from django.db import models

from allele.models import Allele

CHROMOSOMAL_MAPPING_ORDER = {
    "DPB2": 0,
    "DPA2": 1,
    "DPB1": 2,
    "DPA1": 3,
    "DOA": 4,
    "DMA": 5,
    "DMB": 6,
    "Z": 7,
    "TAP1": 8,
    "TAP2": 9,
    "DOB": 10,
    "DQB2": 11,
    "DQA2": 12,
    "DQB3": 13,
    "DQB1": 14,
    "DQA1": 15,
    "C": 16,
    "B": 17,
    "S": 18,
    "MICA": 19,
    "MICB": 20,
    "DRA": 21,
    "DRB9": 22,
    "DRB3..DRB8": 23,
    "DRB2": 24,
    "DRB1": 25,
    "E": 26,
    "N": 27,
    "L": 28,
    "J": 29,
    "R": 30,
    "Y": 31,
    "W": 32,
    "A": 33,
    "U": 34,
    "K": 35,
    "T": 36,
    "H": 37,
    "G": 38,
    "P": 39,
    "V": 40,
    "F": 41,
    "HFE": 42,
}


class Haplotype(models.Model):
    """Contains information about a haplotype that has been added to the HCI."""

    name = models.CharField(
        blank=True,
        default="",
        max_length=300,
        unique=True,
        verbose_name="Name",
        help_text="The name of the HLA haplotype in chromosomal mapping order.",
    )
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
        help_text=(
            "The constituent alleles of the haplotype. "
            "Saved in chromosomal mapping order."
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

    def __str__(self) -> str:
        """Returns a string representation of a specific haplotype."""
        return self.name
