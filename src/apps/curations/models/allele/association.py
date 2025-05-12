"""Defines the model for an allele association.

An allele association is a set of evidence about a disease-allele relationship derived
from a single publication.
"""

from django.db import models

from apps.curations.models.allele.curation import AlleleCuration
from apps.publications.models import PubMedArticle
from constants import HumanReadableIDPrefixConstants as HRIDPrefixes
from constants import ModelsConstants


class AlleleAssociation(models.Model):
    """Contains the top-level information about an allele association."""

    association_id: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_HUMAN_READABLE_ID,
        unique=True,
        editable=False,
        blank=True,
        null=True,
        verbose_name="Association ID",
        help_text="A unique identifier for the association for use in the HCI.",
    )

    is_included_for_scoring: models.BooleanField = models.BooleanField(
        default=False,
        verbose_name="Include",
        help_text="Should this association be included for scoring?",
    )
    is_conflicting_evidence: models.BooleanField = models.BooleanField(
        default=False,
        verbose_name="Conflicts",
        help_text="Is the evidence in this association conflicting?",
    )

    zygosity: models.CharField = models.CharField(
        max_length=ModelsConstants.MAX_LENGTH_ZYGOSITY,
        choices=ModelsConstants.CHOICES_ZYGOSITY,
        default=ModelsConstants.CHOICES_ZYGOSITY[0][0],
    )

    phase_is_confirmed: models.BooleanField = models.BooleanField(
        default=False,
        verbose_name="Phase confirmed",
        help_text="Was the HLA allele phased?",
    )

    typing_methods: models.CharField = models.CharField(
        default=None,
        blank=True,
        null=True,
        verbose_name="Typing Method",
        help_text="What HLA typing methodology was used?",
        max_length=ModelsConstants.MAX_LENGTH_TYPING_METHODS,
        choices=ModelsConstants.CHOICES_TYPING_METHODS,
    )

    class Meta:
        """Defines metadata options."""

        verbose_name = "Allele Association"
        verbose_name_plural = "Allele Associations"

    def __str__(self) -> str:
        """Returns a string representation of the association."""
        if self.association_id:
            return self.association_id
        return f"Allele Association (ID: {self.id if self.id else 'Not Saved Yet'})"  # pyright: ignore[reportAttributeAccessIssue] (Pyright and Django don't play nicely together here.)

    def save(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003 (Since we're overriding the method, I don't think type hints matter.)
        """Saves the association.

        If a human-readable ID hasn't been created for this association, this method
        will create one.
        """
        super().save(*args, **kwargs)
        if not self.association_id:
            prefix = HRIDPrefixes.ALLELE_ASSOCIATION
            self.association_id = f"{prefix}-{self.id:06d}"  # type: ignore (Django and Pyright aren't playing together nicely here.)
            self.save(update_fields=["association_id"])


class PubMedAlleleAssociation(AlleleAssociation):
    """Contains the top-level information about a PubMed allele association."""

    pubmed_article: models.ForeignKey = models.ForeignKey(
        PubMedArticle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="PubMed Article",
    )

    curation: models.ForeignKey = models.ForeignKey(
        AlleleCuration, on_delete=models.CASCADE, related_name="pubmed_associations"
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride] (We want to override the parent's `Meta` class.)
        """Defines metadata options."""

        verbose_name = "PubMed Allele Association"
        verbose_name_plural = "PubMed Allele Associations"
