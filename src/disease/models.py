"""Houses database models for the disease app."""

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from disease.constants.models import DISEASE_TYPE_CHOICES, DiseaseTypes
from disease.validators.models import validate_disease_type_mondo, validate_mondo_id


class Disease(models.Model):
    """Contains information about a disease that has been added to the HCI."""

    slug = models.SlugField(
        default="",
        max_length=7,
        verbose_name="Human-Readable ID",
        help_text="The human-readable ID for the object.",
    )
    disease_type = models.CharField(
        blank=True,
        choices=DISEASE_TYPE_CHOICES,
        default=DiseaseTypes.MONDO,
        max_length=3,
        verbose_name="Disease Type",
        help_text=(
            "The disease ontology type. Only Mondo diseases are supported for now."
        ),
    )
    mondo_id = models.CharField(
        blank=False,
        default="",
        max_length=26,  # A Mondo ID is of the form MONDO:1234567. 13 characters.
        unique=True,
        verbose_name="Mondo ID",
        help_text="The Mondo Disease Ontology ID, e.g., MONDO:1234567.",
    )
    iri = models.CharField(
        blank=True,
        default="",
        max_length=88,  # A typical disease IRI is 44 characters long.
        verbose_name="Internationalized Resource Identifier (IRI)",
    )
    name = models.CharField(
        blank=True,
        default="",
        max_length=256,
        verbose_name="Name",
        help_text="The name of the disease.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="diseases_added",
        verbose_name="Added By",
        help_text="The user who added the disease.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the disease was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "disease"
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"

    def __str__(self) -> str:
        """Returns a string representation of the disease."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Adds a human-readable ID."""
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f"D{self.id:06d}"
            self.save(update_fields=["slug"])

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific disease."""
        return reverse("disease-detail", kwargs={"slug": self.slug})

    def clean(self) -> None:
        """Makes sure the disease is valid."""
        super().clean()
        validate_disease_type_mondo(self)
        validate_mondo_id(self)
