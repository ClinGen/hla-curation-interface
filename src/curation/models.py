"""Houses database models for the curation app."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse

from allele.models import Allele
from curation.constants.models.common import STATUS_CHOICES, Status
from curation.constants.models.curation import (
    CLASSIFICATION_CHOICES,
    CURATION_TYPE_CHOICES,
    Classification,
    CurationTypes,
)
from curation.constants.models.evidence import (
    ADDITIONAL_PHENOTYPES_CHOICES,
    EFFECT_SIZE_STATISTIC_CHOICES,
    MULTIPLE_TESTING_CORRECTION_CHOICES,
    TYPING_METHOD_CHOICES,
    ZYGOSITY_CHOICES,
    AdditionalPhenotypes,
    EffectSizeStatistic,
    MultipleTestingCorrection,
    TypingMethod,
    Zygosity,
)
from curation.constants.score import Intervals, Points
from curation.interval import Interval
from curation.validators.models.curation import (
    validate_classification,
    validate_curation_type,
    validate_status,
)
from curation.validators.models.evidence import (
    validate_beta_string,
    validate_ci_end_string,
    validate_ci_start_string,
    validate_effect_size_statistic,
    validate_odds_ratio_string,
    validate_p_value_string,
    validate_publication,
    validate_relative_risk_string,
    validate_typing_method,
)
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication


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

    def clean(self) -> None:
        """Makes sure the curation is saved in a valid state."""
        super().clean()
        validate_status(self)
        validate_curation_type(self)
        validate_classification(self)

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


class Demographic(models.Model):
    """Contains the biogeographic groups in Huddart et al. 2019.

    There is a fixture in the fixtures directory that can be used to load the groups
    into the database.
    """

    group = models.CharField(
        blank=False,
        max_length=20,  # Accommodates the human-readable group name.
        unique=True,
        verbose_name="Group",
        help_text="The bio-geographical group for a population.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "demographic"
        verbose_name = "Demographic"
        verbose_name_plural = "Demographics"

    def __str__(self) -> str:
        """Returns a string representation of the demographic."""
        return self.group


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
    demographics = models.ManyToManyField(
        Demographic,
        blank=True,
        db_table="evidence_demographic_map",
        related_name="evidence",
        help_text="The biogeographic groups for the populations in the evidence.",
    )
    demographics_notes = models.TextField(
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
    has_association = models.BooleanField(
        default=True,
        verbose_name="Weighing Association",
        help_text="Is there a significant association with the disease?",
    )
    has_association_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
    )
    needs_review = models.BooleanField(
        default=False,
        verbose_name="Needs Manual Review",
        help_text="Does this evidence need to be reviewed manually?",
    )
    needs_review_notes = models.TextField(
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

    def clean(self) -> None:
        """Makes sure the data being submitted is valid."""
        validate_publication(self)
        validate_typing_method(self)
        validate_p_value_string(self)
        validate_effect_size_statistic(self)
        validate_odds_ratio_string(self)
        validate_relative_risk_string(self)
        validate_beta_string(self)
        validate_ci_start_string(self)
        validate_ci_end_string(self)

    @property
    def num_fields(self) -> int:
        """Returns the number of fields.

        If the curation is an allele curation, this returns the number of fields in
        the allele. If the curation is a haplotype curation, this returns the number
        of fields in the allele with the lowest number of fields.
        """
        num_fields = 1  # Default to the lowest possible number of fields to be safe.
        if (
            self.curation
            and self.curation.curation_type == CurationTypes.ALLELE
            and self.curation.allele
        ):
            num_fields = self.curation.allele.name.count(":") + 1
        elif (
            self.curation
            and self.curation.curation_type == CurationTypes.HAPLOTYPE
            and self.curation.haplotype
        ):
            large_int = 1000
            min_num_fields = large_int
            for allele in self.curation.haplotype.alleles.all():
                allele_num_fields = allele.name.count(":") + 1
                if allele_num_fields < min_num_fields:
                    min_num_fields = allele_num_fields
            if min_num_fields != large_int:
                num_fields = min_num_fields
        return num_fields

    @property
    def score(self) -> float:
        """Returns the score for the evidence."""
        return self.score_before_multipliers * self.score_step_6a * self.score_step_6b

    @property
    def score_before_multipliers(self) -> float:
        """Returns the score for the evidence before multipliers are applied."""
        return (
            self.score_step_1
            + (self.score_step_2 if self.score_step_2 else 0)
            + self.score_step_3
            + (self.score_step_4 if self.score_step_4 else 0)
            + self.score_step_5
        )

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
        score = {
            1: Points.S1B_1_FIELD,
            2: Points.S1B_2_FIELD,
            3: Points.S1B_3_FIELD,
            4: Points.S1B_4_FIELD,
        }
        return score.get(self.num_fields)

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
    def score_step_2(self) -> float | None:
        """Returns the score for step 2."""
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
            return typing_method_points.get(self.typing_method)
        return None

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
            (Intervals.S3A.GWAS_1, Points.S3A_INTERVAL_1),
            (Intervals.S3A.GWAS_2, Points.S3A_INTERVAL_2),
            (Intervals.S3A.GWAS_3, Points.S3A_INTERVAL_3),
            (Intervals.S3A.GWAS_4, Points.S3A_INTERVAL_4),
            (Intervals.S3A.GWAS_5, Points.S3A_INTERVAL_5),
        ]

        non_gwas_intervals = [
            (Intervals.S3A.NON_GWAS_1, Points.S3A_INTERVAL_1),
            (Intervals.S3A.NON_GWAS_2, Points.S3A_INTERVAL_2),
            (Intervals.S3A.NON_GWAS_3, Points.S3A_INTERVAL_3),
            (Intervals.S3A.NON_GWAS_4, Points.S3A_INTERVAL_4),
            (Intervals.S3A.NON_GWAS_5, Points.S3A_INTERVAL_5),
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
            if not confidence_interval.contains(Decimal("1.0")):
                return Points.S3C_CI_DOES_NOT_CROSS
        if has_stat and stat_is_beta and has_ci:
            confidence_interval = Interval(
                start=self.ci_start,  # type: ignore
                end=self.ci_end,  # type: ignore
                start_inclusive=True,
                end_inclusive=True,
                variable="CI",
            )
            if not confidence_interval.contains(Decimal("0.0")):
                return Points.S3C_CI_DOES_NOT_CROSS
        return None

    @property
    def score_step_4(self) -> float | None:  # noqa: C901
        """Returns the score for step 4."""
        if self.cohort_size is None:
            return None

        gwas_intervals = [
            (Intervals.S4.GWAS_1, Points.S4_INTERVAL_1),
            (Intervals.S4.GWAS_2, Points.S4_INTERVAL_2),
            (Intervals.S4.GWAS_3, Points.S4_INTERVAL_3),
            (Intervals.S4.GWAS_4, Points.S4_INTERVAL_4),
            (Intervals.S4.GWAS_5, Points.S4_INTERVAL_5),
        ]

        non_gwas_intervals = [
            (Intervals.S4.NON_GWAS_1, Points.S4_INTERVAL_1),
            (Intervals.S4.NON_GWAS_2, Points.S4_INTERVAL_2),
            (Intervals.S4.NON_GWAS_3, Points.S4_INTERVAL_3),
            (Intervals.S4.NON_GWAS_4, Points.S4_INTERVAL_4),
            (Intervals.S4.NON_GWAS_5, Points.S4_INTERVAL_5),
        ]

        intervals = gwas_intervals if self.is_gwas else non_gwas_intervals

        for interval, points in intervals:
            if interval.contains(Decimal(self.cohort_size)):
                return points
        return None

    @property
    def score_step_5(self) -> float:
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
        return 0.0

    @property
    def score_step_6a(self) -> int:
        """Returns the score for step 6A."""
        if self.has_association:
            return Points.S6A_ASSOCIATION
        return Points.S6A_NO_ASSOCIATION

    @property
    def score_step_6b(self) -> float:
        """Returns the score for step 6B."""
        if self.num_fields == 1:
            return Points.S6B_1_FIELD
        return Points.S6B_MORE_THAN_1_FIELD
