"""Houses database models for the curation app."""

from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele
from curation.score import (
    Interval,
    Points,
    step_3a_gwas_interval_1,
    step_3a_gwas_interval_2,
    step_3a_gwas_interval_3,
    step_3a_gwas_interval_4,
    step_3a_gwas_interval_5,
    step_3a_non_gwas_interval_1,
    step_3a_non_gwas_interval_2,
    step_3a_non_gwas_interval_3,
    step_3a_non_gwas_interval_4,
    step_3a_non_gwas_interval_5,
    step_4_gwas_interval_1,
    step_4_gwas_interval_2,
    step_4_gwas_interval_3,
    step_4_gwas_interval_4,
    step_4_gwas_interval_5,
    step_4_non_gwas_interval_1,
    step_4_non_gwas_interval_2,
    step_4_non_gwas_interval_3,
    step_4_non_gwas_interval_4,
    step_4_non_gwas_interval_5,
)
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication


class Status:
    """Defines the status codes for curations and evidence."""

    IN_PROGRESS = "INP"
    DONE = "DNE"


STATUS_CHOICES = {
    Status.IN_PROGRESS: "In Progress",
    Status.DONE: "Done",
}


class CurationTypes:
    """Defines the curation type codes."""

    ALLELE = "ALL"
    HAPLOTYPE = "HAP"


CURATION_TYPE_CHOICES = {
    CurationTypes.ALLELE: "Allele",
    CurationTypes.HAPLOTYPE: "Haplotype",
}


class Classification:
    """Defines the classification codes for a curation."""

    DEFINITIVE = "DEF"
    STRONG = "STR"
    MODERATE = "MOD"
    LIMITED = "LIM"
    NO_KNOWN = "NOK"
    DISPUTED = "DIS"
    REFUTED = "REF"


CLASSIFICATION_CHOICES = {
    Classification.DEFINITIVE: "Definitive",
    Classification.STRONG: "Strong",
    Classification.MODERATE: "Moderate",
    Classification.LIMITED: "Limited",
    Classification.NO_KNOWN: "No Known Association",
    Classification.DISPUTED: "Disputed",
    Classification.REFUTED: "Refuted",
}


class Curation(models.Model):
    """Contains top-level information about a curation."""

    status = models.CharField(
        blank=False,
        choices=STATUS_CHOICES,
        default=Status.IN_PROGRESS,
        max_length=3,
        verbose_name="Status",
        help_text=(
            f"Either '{Status.IN_PROGRESS}' (in progress) or '{Status.DONE}' (done)."
        ),
    )
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
    classification = models.CharField(
        blank=False,
        choices=CLASSIFICATION_CHOICES,
        default=Classification.NO_KNOWN,
        max_length=3,
        verbose_name="Classification",
        help_text="The classification level for the curation.",
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

    def clean(self) -> None:  # noqa: C901 (Locality of behavior wins out here.)
        """Makes sure the curation is saved in a valid state.

        - Makes sure the curation has an allele or haplotype
        - Makes sure that haplotype information isn't added to an allele curation
          and vice versa.
        - Makes sure a curation can't be marked as done if it has in-progress evidence.
        - Makes sure the classification is correct given the score.

        Raises:
            ValidationError: If the curation isn't in a valid state.
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
        if self.status == Status.DONE:
            for evidence in self.evidence.all():
                if evidence.status == Status.IN_PROGRESS and evidence.is_included:
                    raise ValidationError(
                        {"status": "All included evidence must be marked as done."}
                    )
        if self.pk:
            if self.classification == Classification.NO_KNOWN and self.score != 0:
                raise ValidationError({"classification": "Score must be 0."})
            if self.classification == Classification.LIMITED and self.score >= 25:
                raise ValidationError({"classification": "Score must be less than 25."})
            if self.classification == Classification.MODERATE and not (
                25 <= self.score <= 50
            ):
                raise ValidationError({"classification": "Score must be in 25-50."})
            if self.classification == Classification.STRONG and self.score < 50:
                raise ValidationError(
                    {"classification": "Score must be greater than 50."}
                )
            if self.classification == Classification.DEFINITIVE and self.score < 50:
                raise ValidationError(
                    {"classification": "Score must be greater than 50."}
                )

    @property
    def score(self) -> float:
        """Returns the score for the curation."""
        total = 0.0
        for evidence in self.evidence.all():
            if evidence.is_included and evidence.is_conflicting:
                total -= evidence.score
            elif evidence.is_included and not evidence.is_conflicting:
                total += evidence.score
        return total


class Zygosity:
    """Defines zygosity status codes."""

    MONOALLELIC = "MO"
    BIALLELIC = "BI"


ZYGOSITY_CHOICES = {
    Zygosity.MONOALLELIC: "Monoallelic (heterozygous)",
    Zygosity.BIALLELIC: "Biallelic (homozygous)",
}


class TypingMethod:
    """Defines typing method codes."""

    TAG_SNPS = "TAG"
    MICROARRAYS = "MIC"
    SEROLOGICAL = "SER"
    IMPUTATION = "IMP"
    LOW_RES_TYPING = "LRT"
    HIGH_RES_TYPING = "HRT"
    WHOLE_EXOME_SEQ = "WES"
    RNA_SEQ = "RNA"
    SANGER_SEQ = "SBT"
    WHOLE_GENE_SEQ = "WGN"
    WHOLE_GENOME_SEQ = "WGS"
    NEXT_GENERATION_SEQ = "NGS"
    LONG_READ_SEQ = "LRS"


TYPING_METHOD_CHOICES = {
    TypingMethod.TAG_SNPS: "Tagging / Tag SNPs",
    TypingMethod.MICROARRAYS: "Microarrays",
    TypingMethod.SEROLOGICAL: "Serological Typing",
    TypingMethod.IMPUTATION: "Imputation",
    TypingMethod.LOW_RES_TYPING: "Low-Resolution Molecular Genotyping",
    TypingMethod.HIGH_RES_TYPING: "High-Resolution Molecular Genotyping",
    TypingMethod.WHOLE_EXOME_SEQ: "Whole Exome Sequencing",
    TypingMethod.RNA_SEQ: "RNA Sequencing",
    TypingMethod.SANGER_SEQ: "Sanger-Sequencing-Based Typing",
    TypingMethod.WHOLE_GENOME_SEQ: "Whole Genome Sequencing",
    TypingMethod.NEXT_GENERATION_SEQ: "Next Generation Sequencing",
    TypingMethod.LONG_READ_SEQ: "Long Read Sequencing",
}


class MultipleTestingCorrection:
    """Defines codes for multiple testing correction."""

    OVERALL = "OVR"
    TWO_STEP = "TWO"


MULTIPLE_TESTING_CORRECTION_CHOICES = {
    MultipleTestingCorrection.OVERALL: "Overall Correction for Multiple Testing",
    MultipleTestingCorrection.TWO_STEP: "2-step p-value Correction",
}


class EffectSizeStatistic:
    """Defines the effect size statistic codes."""

    ODDS_RATIO = "OR"
    RELATIVE_RISK = "RR"
    BETA = "BE"
    OTHER = "OT"


EFFECT_SIZE_STATISTIC_CHOICES = {
    EffectSizeStatistic.ODDS_RATIO: "Odds Ratio (OR)",
    EffectSizeStatistic.RELATIVE_RISK: "Relative Risk (RR)",
    EffectSizeStatistic.BETA: "Beta",
    EffectSizeStatistic.OTHER: "Other",
}


class AdditionalPhenotypes:
    """Defines the codes for the additional phenotypes options."""

    SPECIFIC_DISEASE_RELATED = "SDR"
    ONLY_DISEASE_TESTED = "ODT"


ADDITIONAL_PHENOTYPES_CHOICES = {
    AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED: "Has specific disease-related phenotype",
    AdditionalPhenotypes.ONLY_DISEASE_TESTED: "Only disease tested",
}


class Evidence(models.Model):
    """Contains evidence derived from a publication."""

    status = models.CharField(
        blank=False,
        choices=STATUS_CHOICES,
        default=Status.IN_PROGRESS,
        max_length=3,
        verbose_name="Status",
        help_text=(
            f"Either '{Status.IN_PROGRESS}' (in progress) or '{Status.DONE}' (done)."
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
    is_gwas_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    zygosity = models.CharField(
        choices=ZYGOSITY_CHOICES,
        default=Zygosity.MONOALLELIC,
        max_length=2,
        verbose_name="Zygosity",
        help_text="Either monoallelic (homozygous) or biallelic (heterozygous).",
    )
    zygosity_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    phase_confirmed = models.BooleanField(
        default=False,
        verbose_name="Phase Confirmed",
        help_text="Is the chromosomal phase between alleles at different loci known?",
    )
    phase_confirmed_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    typing_method = models.CharField(
        blank=True,
        choices=TYPING_METHOD_CHOICES,
        default="",
        max_length=3,
        verbose_name="Typing Method",
        help_text="The typing method used to determine HLA sequence.",
    )
    typing_method_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    p_value_string = models.CharField(
        blank=True,
        default="",
        max_length=40,
        verbose_name="p-value",
        help_text=(
            "The reported p-value as a decimal (e.g. 0.05) or in scientific "
            "notation (e.g. 5e-8)."
        ),
    )
    p_value = models.DecimalField(
        decimal_places=30,
        max_digits=40,
        null=True,
        verbose_name="p-value Decimal",
        help_text="The p-value represented as a decimal.",
    )
    p_value_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    multiple_testing_correction = models.CharField(
        blank=True,
        choices=MULTIPLE_TESTING_CORRECTION_CHOICES,
        default="",
        max_length=3,
        verbose_name="Multiple Testing Correction",
        help_text="Correction for multiple hypothesis testing.",
    )
    multiple_testing_correction_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    effect_size_statistic = models.CharField(
        blank=True,
        choices=EFFECT_SIZE_STATISTIC_CHOICES,
        default="",
        max_length=3,
        verbose_name="Effect Size Statistic",
        help_text="Select a statistic for the effect size.",
    )
    effect_size_statistic_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    odds_ratio_string = models.CharField(
        blank=True,
        default="",
        max_length=10,
        verbose_name="Odds Ratio (OR)",
        help_text="The odds ratio as a decimal (e.g. 0.5).",
    )
    odds_ratio = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name="Odds Ratio (OR) Decimal",
        help_text="The odds ratio represented as a decimal.",
    )
    relative_risk_string = models.CharField(
        blank=True,
        default="",
        max_length=10,
        verbose_name="Relative Risk (RR)",
        help_text="The relative risk as a decimal (e.g. 0.5).",
    )
    relative_risk = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name="Relative Risk (RR) Decimal",
        help_text="The relative risk represented as a decimal.",
    )
    beta_string = models.CharField(
        blank=True,
        default="",
        max_length=10,
        verbose_name="Beta Coefficient",
        help_text="The beta coefficient as a decimal (e.g. 0.5).",
    )
    beta = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name="Beta Coefficient",
        help_text="The beta coefficient represented as a decimal.",
    )
    ci_start_string = models.CharField(
        blank=True,
        default="",
        max_length=10,
        verbose_name="Confidence Interval Start",
        help_text="The start of the confidence interval as a decimal (e.g. 0.5).",
    )
    ci_start = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name="Confidence Interval Start Decimal",
        help_text="The confidence interval start represented as a decimal.",
    )
    ci_end_string = models.CharField(
        blank=True,
        default="",
        max_length=10,
        verbose_name="Confidence Interval End",
        help_text="The end of the confidence interval as a decimal (e.g. 0.5).",
    )
    ci_end = models.DecimalField(
        decimal_places=5,
        max_digits=10,
        null=True,
        verbose_name="Confidence Interval End Decimal",
        help_text="The confidence interval end represented as a decimal.",
    )
    ci_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    cohort_size = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Cohort Size",
        help_text="The number of cases added to the number of controls.",
    )
    cohort_size_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    additional_phenotypes = models.CharField(
        blank=True,
        choices=ADDITIONAL_PHENOTYPES_CHOICES,
        default="",
        max_length=3,
        verbose_name="Additional Phenotypes",
        help_text="Whether there is a specific disease-related phenotype.",
    )
    additional_phenotypes_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
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

    def clean_effect_size_statistic(self) -> None:
        """Makes sure there is only one effect size statistic."""
        if self.effect_size_statistic == EffectSizeStatistic.ODDS_RATIO:
            self.relative_risk_string = ""
            self.relative_risk = None
            self.beta_string = ""
            self.beta = None
        elif self.effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK:
            self.odds_ratio_string = ""
            self.odds_ratio = None
            self.beta_string = ""
            self.beta = None
        elif self.beta_string == EffectSizeStatistic.BETA:
            self.relative_risk_string = ""
            self.relative_risk = None
            self.odds_ratio_string = ""
            self.odds_ratio = None

    def clean_p_value_string(self) -> None:
        """Makes sure the p-value string is valid.

        Raises:
             ValidationError: When we can't convert the p-value string to a decimal.
        """
        if self.p_value_string != "":
            try:
                Decimal(self.p_value_string)
            except InvalidOperation as exc:
                message = (
                    "Unable to save p-value as written. "
                    "Make sure it is written as a decimal (e.g. 0.05) "
                    "or in scientific notation (e.g. 5e-8)."
                )
                raise ValidationError({"p_value_string": message}) from exc

    def clean_odds_ratio_string(self) -> None:
        """Makes sure the odds ratio string is valid.

        Raises:
             ValidationError: When we can't convert the odds ratio string to a decimal.
        """
        if self.odds_ratio_string != "":
            try:
                Decimal(self.odds_ratio_string)
            except InvalidOperation as exc:
                message = (
                    "Unable to save odds ratio as written. "
                    "Make sure it is written as an integer or decimal."
                )
                raise ValidationError({"odds_ratio_string": message}) from exc

    def clean_relative_risk_string(self) -> None:
        """Makes sure the relative risk string is valid.

        Raises:
             ValidationError: When we can't convert the relative risk string to a
                              decimal.
        """
        if self.relative_risk_string != "":
            try:
                Decimal(self.relative_risk_string)
            except InvalidOperation as exc:
                message = (
                    "Unable to save relative risk as written. "
                    "Make sure it is written as an integer or decimal."
                )
                raise ValidationError({"relative_risk_string": message}) from exc

    def clean_beta_string(self) -> None:
        """Makes sure the beta string is valid.

        Raises:
             ValidationError: When we can't convert the beta string to a decimal.
        """
        if self.beta_string != "":
            try:
                Decimal(self.beta_string)
            except InvalidOperation as exc:
                message = (
                    "Unable to save beta coefficient as written. "
                    "Make sure it is written as an integer or decimal."
                )
                raise ValidationError({"beta_string": message}) from exc

    @property
    def score(self) -> float:
        """Returns the score for the evidence."""
        return self.score_step_1 + self.score_step_2 + self.score_step_3

    @property
    def score_step_1(self) -> float:
        """Returns the score for step 1."""
        total = 0.0
        total += self.score_step_1a if self.score_step_1a else 0
        total += self.score_step_1b if self.score_step_1b else 0
        total += self.score_step_1c if self.score_step_1c else 0
        total += self.score_step_1d if self.score_step_1d else 0
        return total

    @property
    def score_step_1a(self) -> float | None:
        """Returns the score for step 1A."""
        if self.curation and self.curation.curation_type == CurationTypes.ALLELE:
            return Points.S1A_ALLELE
        if self.curation and self.curation.curation_type == CurationTypes.HAPLOTYPE:
            return Points.S1A_HAPLOTYPE
        return None

    @property
    def score_step_1b(self) -> float | None:
        """Returns the score for step 1B."""
        if (
            self.curation
            and self.curation.curation_type == CurationTypes.ALLELE
            and self.curation.allele
        ):
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
        """Returns the score for step 1C."""
        if self.zygosity == Zygosity.MONOALLELIC:
            return Points.S1C_MONOALLELIC
        if self.zygosity == Zygosity.BIALLELIC:
            return Points.S1C_BIALLELIC
        return None

    @property
    def score_step_1d(self) -> float:
        """Returns the score for step 1D."""
        if self.phase_confirmed:
            return Points.S1D_PHASE_CONFIRMED
        return Points.S1D_PHASE_NOT_CONFIRMED

    @property
    def score_step_2(self) -> float:
        """Returns the score for step 2."""
        total = 0.0
        typing_method_points = {
            TypingMethod.TAG_SNPS: Points.S2_TAG_SNPS,
            TypingMethod.MICROARRAYS: Points.S2_MICROARRAYS,
            TypingMethod.SEROLOGICAL: Points.S2_SEROLOGICAL,
            TypingMethod.IMPUTATION: Points.S2_IMPUTATION,
            TypingMethod.LOW_RES_TYPING: Points.S2_LOW_RES_TYPING,
            TypingMethod.HIGH_RES_TYPING: Points.S2_HIGH_RES_TYPING,
            TypingMethod.WHOLE_EXOME_SEQ: Points.S2_WHOLE_EXOME_SEQ,
            TypingMethod.RNA_SEQ: Points.S2_RNA_SEQ,
            TypingMethod.SANGER_SEQ: Points.S2_SANGER_SEQ,
            TypingMethod.WHOLE_GENE_SEQ: Points.S2_WHOLE_GENE_SEQ,
            TypingMethod.WHOLE_GENOME_SEQ: Points.S2_WHOLE_GENOME_SEQ,
            TypingMethod.NEXT_GENERATION_SEQ: Points.S2_NEXT_GENERATION_SEQ,
            TypingMethod.LONG_READ_SEQ: Points.S2_LONG_READ_SEQ,
        }
        if self.typing_method != "":
            total += typing_method_points.get(self.typing_method, 0)
        return total

    @property
    def score_step_3(self) -> float:
        """Returns the score for step 3."""
        total = 0.0
        total += self.score_step_3a if self.score_step_3a else 0
        total += self.score_step_3b if self.score_step_3b else 0
        total += self.score_step_3c1 if self.score_step_3c1 else 0
        total += self.score_step_3c2 if self.score_step_3c2 else 0
        return total

    @property
    def score_step_3a(self) -> float | None:  # noqa: C901
        """Returns the score for step 3A."""
        if self.p_value is None:
            return None

        gwas_intervals = [
            (step_3a_gwas_interval_1, Points.S3A_INTERVAL_1),
            (step_3a_gwas_interval_2, Points.S3A_INTERVAL_2),
            (step_3a_gwas_interval_3, Points.S3A_INTERVAL_3),
            (step_3a_gwas_interval_4, Points.S3A_INTERVAL_4),
            (step_3a_gwas_interval_5, Points.S3A_INTERVAL_5),
        ]

        non_gwas_intervals = [
            (step_3a_non_gwas_interval_1, Points.S3A_INTERVAL_1),
            (step_3a_non_gwas_interval_2, Points.S3A_INTERVAL_2),
            (step_3a_non_gwas_interval_3, Points.S3A_INTERVAL_3),
            (step_3a_non_gwas_interval_4, Points.S3A_INTERVAL_4),
            (step_3a_non_gwas_interval_5, Points.S3A_INTERVAL_5),
        ]

        intervals = gwas_intervals if self.is_gwas else non_gwas_intervals

        for interval, points in intervals:
            if interval.contains(self.p_value):
                return points
        return None

    @property
    def score_step_3b(self) -> float | None:
        """Returns the score for step 3B."""
        if self.multiple_testing_correction == "":
            return None
        if self.multiple_testing_correction == MultipleTestingCorrection.OVERALL:
            return Points.S3B_OVERALL
        if self.multiple_testing_correction == MultipleTestingCorrection.TWO_STEP:
            return Points.S3B_TWO_STEP
        return None

    @property
    def score_step_3c1(self) -> float | None:
        """Returns the first score for step 3C."""
        if self.odds_ratio and (self.odds_ratio >= 2 or self.odds_ratio <= 0.5):
            return Points.S3C_OR_RR_BETA
        if self.relative_risk and (
            self.relative_risk >= 2 or self.relative_risk <= 0.5
        ):
            return Points.S3C_OR_RR_BETA
        if self.beta and (self.beta >= 0.5 or self.beta <= -0.5):
            return Points.S3C_OR_RR_BETA
        return None

    @property
    def score_step_3c2(self) -> float | None:
        """Returns the second score for step 3C."""
        has_stat = self.effect_size_statistic
        stat_is_odds_ratio_or_relative_risk = (
            self.effect_size_statistic == EffectSizeStatistic.ODDS_RATIO
            or self.effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK
        )
        stat_is_beta = self.effect_size_statistic == EffectSizeStatistic.BETA
        has_ci = self.ci_start and self.ci_end
        if has_stat and stat_is_odds_ratio_or_relative_risk and has_ci:
            confidence_interval = Interval(
                start=self.ci_start,  # type: ignore
                end=self.ci_end,  # type: ignore
                start_inclusive=True,
                end_inclusive=True,
                variable="CI",
            )
            if not confidence_interval.contains(1):
                return Points.S3C_CI_DOES_NOT_CROSS
        if has_stat and stat_is_beta and has_ci:
            confidence_interval = Interval(
                start=self.ci_start,  # type: ignore
                end=self.ci_end,  # type: ignore
                start_inclusive=True,
                end_inclusive=True,
                variable="CI",
            )
            if not confidence_interval.contains(0):
                return Points.S3C_CI_DOES_NOT_CROSS
        return None

    @property
    def score_step_4(self) -> float | None:  # noqa: C901
        """Returns the score for step 4."""
        if self.cohort_size is None:
            return None

        gwas_intervals = [
            (step_4_gwas_interval_1, Points.S4_INTERVAL_1),
            (step_4_gwas_interval_2, Points.S4_INTERVAL_2),
            (step_4_gwas_interval_3, Points.S4_INTERVAL_3),
            (step_4_gwas_interval_4, Points.S4_INTERVAL_4),
            (step_4_gwas_interval_5, Points.S4_INTERVAL_5),
        ]

        non_gwas_intervals = [
            (step_4_non_gwas_interval_1, Points.S4_INTERVAL_1),
            (step_4_non_gwas_interval_2, Points.S4_INTERVAL_2),
            (step_4_non_gwas_interval_3, Points.S4_INTERVAL_3),
            (step_4_non_gwas_interval_4, Points.S4_INTERVAL_4),
            (step_4_non_gwas_interval_5, Points.S4_INTERVAL_5),
        ]

        intervals = gwas_intervals if self.is_gwas else non_gwas_intervals

        for interval, points in intervals:
            if interval.contains(self.cohort_size):
                return points
        return None

    @property
    def score_step_5(self) -> float | None:
        """Returns the score for step 5."""
        has_additional_phenotypes = self.additional_phenotypes
        has_specific_disease_related = (
            self.additional_phenotypes == AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED
        )
        has_only_disease_tested = (
            self.additional_phenotypes == AdditionalPhenotypes.ONLY_DISEASE_TESTED
        )
        if has_additional_phenotypes and has_specific_disease_related:
            return Points.S5_SPECIFIC_PHENOTYPE
        if has_additional_phenotypes and has_only_disease_tested:
            return Points.S5_ONLY_DISEASE_TESTED
        return None
