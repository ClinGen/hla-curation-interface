from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse
from simple_history.models import HistoricalRecords

from allele.clients import fetch_allele_data, get_car_id


class Allele(models.Model):
    slug = models.SlugField(
        default="",
        max_length=7,
        verbose_name="Human-Readable ID",
        help_text="The human-readable ID for the object.",
    )
    name = models.CharField(
        blank=False,
        default="",
        max_length=60,  # Should be plenty of characters.
        unique=True,
        verbose_name="Name",
        help_text=(
            "The name of the HLA allele, e.g., DRB3*03:01:01. "
            "(The 'HLA-' part should be omitted.)"
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
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When the allele was last updated.",
    )
    history = HistoricalRecords()

    class Meta:
        db_table = "allele"
        verbose_name = "Allele"
        verbose_name_plural = "Alleles"

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args, **kwargs) -> None:
        """Adds a human-readable ID."""
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f"A{self.pk:06d}"
            self.save(update_fields=["slug"])

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        return reverse("allele-detail", kwargs={"slug": self.slug})

    @classmethod
    def get_or_build(cls, name: str) -> "Allele":
        """Returns the allele with the name, or builds an unsaved one from the CAR.

        Args:
            name: The name of the allele, e.g., DRB3*03:01:01.

        Returns:
            The existing allele, or a new unsaved allele with its CAR ID.

        Raises:
            ValidationError: If the allele isn't in the database and fetching it
                from the ClinGen Allele Registry fails.
        """
        existing = cls.objects.filter(name=name).first()
        if existing:
            return existing
        allele_data = fetch_allele_data(name)
        if not allele_data:
            raise ValidationError(
                {
                    "name": (
                        "Oops, something went wrong trying to fetch data from the "
                        "ClinGen Allele Registry. Please try again later."
                    )
                }
            )
        return cls(name=name, car_id=get_car_id(allele_data))

    @property
    def display_name(self) -> str:
        return f"HLA-{self.name}"
