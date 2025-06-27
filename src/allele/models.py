"""Houses database models for the allele app."""

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse


class Allele(models.Model):
    """Contains information about an allele that has been added to the HCI."""

    car_id = models.CharField(
        blank=False,
        default="",
        max_length=28,  # A CAR allele ID is of the form XAHLA718827727. 14 characters.
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
