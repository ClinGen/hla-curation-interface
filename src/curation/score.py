"""Houses code for scoring evidence based on the HLA scoring framework."""

from decimal import Decimal

from curation.constants.models.curation import CurationTypes
from curation.constants.models.evidence import (
    AdditionalPhenotypes,
    EffectSizeStatistic,
    MultipleTestingCorrection,
    TypingMethod,
    Zygosity,
)
from curation.constants.score import Intervals, Points
from curation.interval import Interval


def get_step_1a_points(evidence) -> float | None:
    """Returns the points for step 1A."""
    points = None
    if (
        evidence.curation
        and evidence.curation.curation_type
        and evidence.curation.curation_type == CurationTypes.ALLELE
    ):
        points = Points.S1A_ALLELE
    if (
        evidence.curation
        and evidence.curation.curation_type
        and evidence.curation.curation_type == CurationTypes.HAPLOTYPE
    ):
        points = Points.S1A_HAPLOTYPE
    return points


def get_step_1b_points(evidence) -> float | None:
    """Returns the points for step 1B."""
    fields_points = {
        1: Points.S1B_1_FIELD,
        2: Points.S1B_2_FIELD,
        3: Points.S1B_3_FIELD,
        4: Points.S1B_4_FIELD,
    }
    return fields_points.get(evidence.num_fields, None)


def get_step_1c_points(evidence) -> float | None:
    """Returns the points for step 1C."""
    points = None
    if evidence.zygosity == Zygosity.MONOALLELIC:
        points = Points.S1C_MONOALLELIC
    if evidence.zygosity == Zygosity.BIALLELIC:
        points = Points.S1C_BIALLELIC
    return points


def get_step_1d_points(evidence) -> float | None:
    """Returns the points for step 1D."""
    points = None
    if evidence.phase_confirmed:
        points = Points.S1D_PHASE_CONFIRMED
    if not evidence.phase_confirmed:
        points = Points.S1D_PHASE_NOT_CONFIRMED
    return points


def get_step_2_points(evidence) -> float | None:
    """Returns the points for step 2."""
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
    return typing_method_points.get(evidence.typing_method, None)


def get_step_3a_points(evidence) -> float | None:
    """Returns the points for step 3A."""
    if evidence.p_value is None:
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

    intervals = gwas_intervals if evidence.is_gwas else non_gwas_intervals

    for interval, points in intervals:
        if interval.contains(evidence.p_value):
            return points
    return None


def get_step_3b_points(evidence) -> float | None:
    """Returns the points for step 3B."""
    points = None
    if evidence.multiple_testing_correction == MultipleTestingCorrection.OVERALL:
        points = Points.S3B_OVERALL
    if evidence.multiple_testing_correction == MultipleTestingCorrection.TWO_STEP:
        points = Points.S3B_TWO_STEP
    return points


def get_step_3c1_points(evidence) -> float | None:
    """Returns the first score for step 3C."""
    points = None

    is_odds_ratio = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.ODDS_RATIO
        and evidence.odds_ratio
    )
    if is_odds_ratio:
        in_interval_1 = Intervals.S3C.OR_RR_1.contains(evidence.odds_ratio)
        in_interval_2 = Intervals.S3C.OR_RR_2.contains(evidence.odds_ratio)
        if in_interval_1 or in_interval_2:
            return Points.S3C_OR_RR_BETA

    is_relative_risk = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK
        and evidence.relative_risk
    )
    if is_relative_risk:
        in_interval_1 = Intervals.S3C.OR_RR_1.contains(evidence.relative_risk)
        in_interval_2 = Intervals.S3C.OR_RR_2.contains(evidence.relative_risk)
        if in_interval_1 or in_interval_2:
            return Points.S3C_OR_RR_BETA

    is_beta = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.BETA
        and evidence.beta
    )
    if is_beta:
        in_interval_1 = Intervals.S3C.BETA_1.contains(evidence.beta)
        in_interval_2 = Intervals.S3C.BETA_2.contains(evidence.beta)
        if in_interval_1 or in_interval_2:
            return Points.S3C_OR_RR_BETA

    return points


def get_step_3c2_points(evidence) -> float | None:
    """Returns the second score for step 3C."""
    has_confidence_interval = evidence.ci_start and evidence.ci_end
    if not has_confidence_interval:
        return None
    confidence_interval = Interval(
        start=evidence.ci_start,  # type: ignore
        end=evidence.ci_end,  # type: ignore
        start_inclusive=True,
        end_inclusive=True,
        variable="CI",
    )

    points = None

    is_odds_ratio = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.ODDS_RATIO
        and evidence.odds_ratio
    )
    is_relative_risk = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK
        and evidence.relative_risk
    )
    if is_odds_ratio or is_relative_risk:
        or_rr_does_not_cross_value = Decimal("1.0")
        does_not_cross = not confidence_interval.contains(or_rr_does_not_cross_value)
        if does_not_cross:
            points = Points.S3C_CI_DOES_NOT_CROSS

    is_beta = (
        evidence.effect_size_statistic
        and evidence.effect_size_statistic == EffectSizeStatistic.BETA
        and evidence.beta
    )
    if is_beta:
        beta_does_not_cross_value = Decimal("0.0")
        does_not_cross = not confidence_interval.contains(beta_does_not_cross_value)
        if does_not_cross:
            points = Points.S3C_CI_DOES_NOT_CROSS

    return points


def get_step_4_points(evidence) -> float | None:
    """Returns the points for step 4."""
    if evidence.cohort_size is None:
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

    intervals = gwas_intervals if evidence.is_gwas else non_gwas_intervals

    for interval, points in intervals:
        if interval.contains(Decimal(evidence.cohort_size)):
            return points
    return None


def get_step_5_points(evidence) -> float | None:
    """Returns the points for step 5."""
    points = None

    specific_phenotype = (
        evidence.additional_phenotypes
        and evidence.additional_phenotypes
        == AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED
    )
    if specific_phenotype:
        points = Points.S5_SPECIFIC_PHENOTYPE

    only_disease_tested = (
        evidence.additional_phenotypes
        and evidence.additional_phenotypes == AdditionalPhenotypes.ONLY_DISEASE_TESTED
    )
    if only_disease_tested:
        points = Points.S5_ONLY_DISEASE_TESTED

    return points


def get_step_6a_multiplier(evidence) -> float:
    """Returns the multiplier for step 6a."""
    if evidence.has_association:
        return Points.S6A_ASSOCIATION
    return Points.S6A_NO_ASSOCIATION


def get_step_6b_multiplier(evidence) -> float:
    """Returns the multiplier for step 6b."""
    if evidence.num_fields == 1:
        return Points.S6B_1_FIELD
    return Points.S6B_MORE_THAN_1_FIELD
