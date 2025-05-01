"""Provide a model for diseases."""

from django.db import models


class Mondo(models.Model):
    """A disease is uniquely identified by its Mondo ID.

    The Mondo Disease Ontology (Mondo) aims to harmonize disease definitions across the
    world. A Mondo ID is a unique identifier for a disease. For more information, see:
    https://mondo.monarchinitiative.org
    """

    mondo_id: models.CharField = models.CharField(
        verbose_name="Mondo ID",
        help_text="The Mondo Disease Ontology ID, e.g., MONDO_0005052.",
    )
    label: models.CharField = models.CharField(verbose_name="Label")

    class Meta:
        """Define metadata options."""

        verbose_name = "Disease"
        verbose_name_plural = "Diseases"

    def __str__(self) -> str:
        """Return a string representation of the disease."""
        return f"{self.label} ({self.mondo_id})"
