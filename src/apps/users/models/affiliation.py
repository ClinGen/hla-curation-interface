"""Provide a model for affiliations."""

from django.db import models

from constants import AffiliationsConstants, ModelsConstants


class Affiliation(models.Model):
    """An affiliation is a group of curators working on the same project."""

    affiliation_id: models.CharField = models.CharField(
        max_length=AffiliationsConstants.MAX_LENGTH_ID,
        primary_key=True,
        verbose_name="Affiliation ID",
    )
    affiliation_name: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_NAME,
        verbose_name="Affiliation Name",
    )

    class Meta:
        """Define metadata options."""

        verbose_name = "Affiliation"
        verbose_name_plural = "Affiliations"

    def __str__(self) -> str:
        """Return a string representation of the affiliation."""
        return f"{self.affiliation_name} ({self.affiliation_id})"
