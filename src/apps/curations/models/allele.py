"""Provide a model for allele curations."""

from django.db import models

from apps.diseases.models import Mondo
from apps.markers.models import Allele
from constants import HumanReadableIDPrefixConstants as HRIDPrefixes
from constants import ModelsConstants


class AlleleCuration(models.Model):
    """A curation is the basic information about a classification."""

    curation_id: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_HUMAN_READABLE_ID,
        unique=True,
        editable=False,
        blank=True,
        null=True,
        verbose_name="Curation ID",
        help_text="A unique identifier for the curation for use in the HCI.",
    )
    disease: models.ForeignKey = models.ForeignKey(Mondo, on_delete=models.CASCADE)
    allele: models.ForeignKey = models.ForeignKey(
        Allele, on_delete=models.CASCADE, null=True
    )
    status: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_NAME,
        verbose_name="Status",
        help_text="The status of the curation, e.g., 'new', 'in progress', 'done'.",
        default="new",
    )
    created_at: models.DateTimeField = models.DateTimeField(
        verbose_name="Created At", auto_now_add=True
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        verbose_name="Updated At", auto_now=True
    )

    def __str__(self) -> str:
        """Return a string representation of the curation."""
        return self.curation_id

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003 (Since we're overriding the method, I don't think type hints matter.)
        """Save the curation. Add the human-readable ID if it doesn't exist."""
        super().save(*args, **kwargs)
        if not self.curation_id:
            prefix = HRIDPrefixes.ALLELE_CURATION
            self.curation_id = f"{prefix}-{self.id:06d}"  # type: ignore (Django and Pyright aren't playing together nicely here.)
            self.save(update_fields=["curation_id"])
