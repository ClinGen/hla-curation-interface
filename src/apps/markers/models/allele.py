"""Provide a model for alleles."""

from django.db import models


class Allele(models.Model):
    """An HLA allele."""

    descriptor: models.CharField = models.CharField(
        verbose_name="Descriptor",
        help_text="The HLA allele descriptor, e.g., A*01:01:01:119.",
    )
    car_id: models.CharField = models.CharField(
        verbose_name="ClinGen Allele Registry ID",
        help_text="A unique identifier for the HLA allele, e.g., CAHLA1449130330.",
    )
    car_url: models.URLField = models.URLField(
        verbose_name="ClinGen Allele Registry URL for the HLA Allele",
    )

    class Meta:
        """Define metadata options."""

        verbose_name = "HLA Allele"
        verbose_name_plural = "HLA Alleles"

    def __str__(self) -> str:
        """Return a string representation of the HLA allele."""
        return f"{self.descriptor} ({self.car_id})"
