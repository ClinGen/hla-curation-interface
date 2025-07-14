"""Houses database models for the curation app."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele
from curation.score import Points
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication


class CurationTypes:
    """Defines the curation type codes."""

    ALLELE = "ALL"
    HAPLOTYPE = "HAP"


CURATION_TYPE_CHOICES = {
    CurationTypes.ALLELE: "Allele",
    CurationTypes.HAPLOTYPE: "Haplotype",
}


class Curation(models.Model):
    """Contains top-level information about a curation."""

    curation_type = models.CharField(
        blank=False,
        choices=CURATION_TYPE_CHOICES,
        default=CurationTypes.ALLELE,
        max_length=3,
        verbose_name="Curation Type",
        help_text=(
            f"Either '{CurationTypes.ALLELE}' (allele) or "
            f"'{CurationTypes.HAPLOTYPE}' (haplotype)."
        ),
    )
    allele = models.ForeignKey(
        Allele,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="curations",
        help_text="Select the allele for this curation.",
    )
    haplotype = models.ForeignKey(
        Haplotype,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="curations",
        help_text="Select the haplotype for this curation.",
    )
    disease = models.ForeignKey(
        Disease,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="curations",
        help_text="Select the disease for this curation.",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="curations_added",
        verbose_name="Added By",
        help_text="The user who added the curation.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the curation was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "curation"
        verbose_name = "Curation"
        verbose_name_plural = "Curations"

    def __str__(self) -> str:
        """Returns a string representation of the curation."""
        return f"Curation #{self.pk} ({self.curation_type})"

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for a specific publication."""
        return reverse("curation-detail", kwargs={"curation_pk": self.pk})

    def clean(self) -> None:
        """Makes sure the curation has an allele or haplotype.

        Also makes sure that haplotype information isn't added to an allele curation
        and vice versa.

        Raises:
            ValidationError: When the curation type is allele but the allele for the
                             curation is not provided. Same for haplotype.
        """
        super().clean()
        if self.curation_type == CurationTypes.ALLELE and not self.allele:
            raise ValidationError(
                {"allele": "An allele is required for an allele curation."}
            )
        if self.curation_type == CurationTypes.HAPLOTYPE and not self.haplotype:
            raise ValidationError(
                {"haplotype": "A haplotype is required for a haplotype curation."}
            )
        if self.curation_type == CurationTypes.ALLELE and self.haplotype:
            self.haplotype = None
        if self.curation_type == CurationTypes.HAPLOTYPE and self.allele:
            self.allele = None


class EvidenceStatus:
    """Defines the evidence status codes."""

    IN_PROGRESS = "INP"
    DONE = "DNE"


EVIDENCE_STATUS_CHOICES = {
    EvidenceStatus.IN_PROGRESS: "In Progress",
    EvidenceStatus.DONE: "Done",
}


class Zygosity:
    """Defines zygosity status codes."""

    MONOALLELIC = "MO"
    BIALLELIC = "BI"


ZYGOSITY_CHOICES = {
    Zygosity.MONOALLELIC: "Monoallelic",
    Zygosity.BIALLELIC: "Biallelic",
}


class Evidence(models.Model):
    """Contains evidence derived from a publication."""

    status = models.CharField(
        blank=False,
        choices=EVIDENCE_STATUS_CHOICES,
        default=EvidenceStatus.IN_PROGRESS,
        max_length=3,
        verbose_name="Status",
        help_text=(
            f"Either '{EvidenceStatus.IN_PROGRESS}' (in progress) or "
            f"'{EvidenceStatus.DONE}' (done)."
        ),
    )
    curation = models.ForeignKey(
        Curation,
        null=True,
        on_delete=models.CASCADE,
        related_name="evidence",
        help_text="The curation that the evidence belongs to.",
    )
    publication = models.ForeignKey(
        Publication,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="evidence",
        help_text="The publication that the evidence comes from.",
    )
    is_conflicting = models.BooleanField(
        default=False,
        verbose_name="Conflicts",
        help_text="Is the evidence in this association conflicting?",
    )
    is_included = models.BooleanField(
        default=False,
        verbose_name="Include",
        help_text="Should this evidence be included for scoring?",
    )
    is_gwas = models.BooleanField(
        default=False,
        verbose_name="GWAS",
        help_text="Was the study a genome-wide association study?",
    )
    zygosity = models.CharField(
        choices=ZYGOSITY_CHOICES,
        default=Zygosity.MONOALLELIC,
        max_length=2,
        verbose_name="Zygosity",
        help_text="Either monoallelic (homozygous) or biallelic (heterozygous).",
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="evidence_added",
        verbose_name="Added By",
        help_text="The user who added the evidence.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the evidence was added.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "evidence"
        verbose_name = "evidence"
        verbose_name_plural = "Evidence"

    def __str__(self) -> str:
        """Returns a string representation of the curation."""
        return f"Evidence #{self.pk}"

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        """Returns the details page for an evidence item."""
        curation_pk = self.curation.pk if self.curation else None
        return reverse(
            "evidence-detail",
            kwargs={
                "curation_pk": curation_pk,
                "evidence_pk": self.pk,
            },
        )

    @property
    def score(self) -> float:
        """Returns the score for the evidence."""
        return self.score_step_1

    @property
    def score_step_1(self) -> float:
        """Returns the score for step 1."""
        total = 0
        total += self.score_step_1a if self.score_step_1a else 0
        total += self.score_step_1b if self.score_step_1b else 0
        total += self.score_step_1c if self.score_step_1c else 0
        return total

    @property
    def score_step_1a(self) -> float | None:
        """Returns the score for step 1A."""
        if self.curation.curation_type == CurationTypes.ALLELE:
            return Points.S1A_ALLELE
        if self.curation.curation_type == CurationTypes.HAPLOTYPE:
            return Points.S1A_HAPLOTYPE
        return None

    @property
    def score_step_1b(self) -> float | None:
        """Returns the score for step 1B."""
        if self.curation.curation_type == CurationTypes.ALLELE:
            num_fields = self.curation.allele.name.count(":") + 1
            score = {
                1: Points.S1B_1_FIELD,
                2: Points.S1B_2_FIELD,
                3: Points.S1B_3_FIELD,
                4: Points.S1B_4_FIELD,
            }
            return score.get(num_fields)
        return None

    @property
    def score_step_1c(self) -> float | None:
        """Returns the score for step 1B."""
        if self.zygosity == Zygosity.MONOALLELIC:
            return Points.S1C_MONOALLELIC
        if self.zygosity == Zygosity.BIALLELIC:
            return Points.S1C_BIALLELIC
        return None
