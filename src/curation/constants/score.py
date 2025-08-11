"""Houses constants used in the curation app's score module."""

from decimal import Decimal

from curation.interval import Interval


class Points:
    """Defines the points for the steps."""

    S1A_ALLELE = 0.0
    S1A_HAPLOTYPE = 2.0
    S1B_1_FIELD = 0.0
    S1B_2_FIELD = 1.0
    S1B_3_FIELD = 2.0
    S1B_4_FIELD = 3.0
    S1C_MONOALLELIC = 0.0
    S1C_BIALLELIC = 0.5
    S1D_PHASE_NOT_CONFIRMED = 0.0
    S1D_PHASE_CONFIRMED = 0.5
    S2_TAG_SNPS = 0.0
    S2_MICROARRAYS = 0.0
    S2_SEROLOGICAL = 1.0
    S2_IMPUTATION = 2.0
    S2_LOW_RES_TYPING = 3.0
    S2_HIGH_RES_TYPING = 3.0
    S2_WHOLE_EXOME_SEQ = 3.0
    S2_RNA_SEQ = 3.0
    S2_SANGER_SEQ = 4.0
    S2_WHOLE_GENE_SEQ = 4.0
    S2_WHOLE_GENOME_SEQ = 5.0
    S2_NEXT_GENERATION_SEQ = 5.0
    S2_LONG_READ_SEQ = 5.0
    S3A_INTERVAL_1 = 0.0
    S3A_INTERVAL_2 = 0.5
    S3A_INTERVAL_3 = 1.0
    S3A_INTERVAL_4 = 1.5
    S3A_INTERVAL_5 = 2.0
    S3B_OVERALL = 1.0
    S3B_TWO_STEP = 2.0
    S3C_OR_RR_BETA = 1.0
    S3C_CI_DOES_NOT_CROSS = 1.0
    S4_INTERVAL_1 = 0.0
    S4_INTERVAL_2 = 1.0
    S4_INTERVAL_3 = 2.0
    S4_INTERVAL_4 = 3.0
    S4_INTERVAL_5 = 4.0
    S5_SPECIFIC_PHENOTYPE = 2.0
    S5_ONLY_DISEASE_TESTED = 0.0
    S6A_ASSOCIATION = 1.0
    S6A_NO_ASSOCIATION = 0.0
    S6B_1_FIELD = 0.5
    S6B_MORE_THAN_1_FIELD = 1.0


class Step3AIntervals:
    """Defines intervals for scoring step 3A."""

    def __init__(self) -> None:
        """Sets the intervals based on the framework."""
        self.GWAS_1 = Interval(
            start=Decimal("1e-4"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.GWAS_2 = Interval(
            start=Decimal("5e-8"),
            end=self.GWAS_1.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.GWAS_3 = Interval(
            start=Decimal("1e-11"),
            end=self.GWAS_2.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.GWAS_4 = Interval(
            start=Decimal("1e-14"),
            end=self.GWAS_3.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.GWAS_5 = Interval(
            start=Decimal("-Infinity"),
            end=self.GWAS_4.start,
            start_inclusive=False,
            end_inclusive=False,
            variable="p-value",
        )
        self.NON_GWAS_1 = Interval(
            start=Decimal("0.05"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.NON_GWAS_2 = Interval(
            start=Decimal("0.01"),
            end=self.NON_GWAS_1.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.NON_GWAS_3 = Interval(
            start=Decimal("0.0005"),
            end=self.NON_GWAS_2.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.NON_GWAS_4 = Interval(
            start=Decimal("0.0001"),
            end=self.NON_GWAS_3.start,
            start_inclusive=True,
            end_inclusive=False,
            variable="p-value",
        )
        self.NON_GWAS_5 = Interval(
            start=Decimal("-Infinity"),
            end=self.NON_GWAS_4.start,
            start_inclusive=False,
            end_inclusive=False,
            variable="p-value",
        )


class Step3CIntervals:
    """Defines intervals for scoring step 3C."""

    def __init__(self) -> None:
        """Sets the intervals based on the framework."""
        self.OR_RR_1 = Interval(
            start=Decimal("2.0"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="OR/RR",
        )
        self.OR_RR_2 = Interval(
            start=Decimal("-Infinity"),
            end=Decimal("0.5"),
            start_inclusive=False,
            end_inclusive=True,
            variable="OR/RR",
        )
        self.BETA_1 = Interval(
            start=Decimal("0.5"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="Beta",
        )
        self.BETA_2 = Interval(
            start=Decimal("-Infinity"),
            end=Decimal("-0.5"),
            start_inclusive=False,
            end_inclusive=True,
            variable="Beta",
        )


class Step4Intervals:
    """Defines intervals for scoring step 4."""

    def __init__(self) -> None:
        """Sets the intervals based on the framework."""
        self.GWAS_1 = Interval(
            start=Decimal("-Infinity"),
            end=Decimal("1000"),
            start_inclusive=False,
            end_inclusive=False,
            variable="size",
        )
        self.GWAS_2 = Interval(
            start=self.GWAS_1.end,
            end=Decimal("2499"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.GWAS_3 = Interval(
            start=self.GWAS_2.end + Decimal("1"),
            end=Decimal("4999"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.GWAS_4 = Interval(
            start=self.GWAS_3.end + Decimal("1"),
            end=Decimal("9999"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.GWAS_5 = Interval(
            start=self.GWAS_4.end + Decimal("1"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="size",
        )
        self.NON_GWAS_1 = Interval(
            start=Decimal("-Infinity"),
            end=Decimal("50"),
            start_inclusive=False,
            end_inclusive=False,
            variable="size",
        )
        self.NON_GWAS_2 = Interval(
            start=self.NON_GWAS_1.end,
            end=Decimal("99"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.NON_GWAS_3 = Interval(
            start=self.NON_GWAS_2.end + Decimal("1"),
            end=Decimal("249"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.NON_GWAS_4 = Interval(
            start=self.NON_GWAS_3.end + Decimal("1"),
            end=Decimal("499"),
            start_inclusive=True,
            end_inclusive=True,
            variable="size",
        )
        self.NON_GWAS_5 = Interval(
            start=self.NON_GWAS_4.end + Decimal("1"),
            end=Decimal("Infinity"),
            start_inclusive=True,
            end_inclusive=False,
            variable="size",
        )


class Intervals:
    """Defines all intervals used in scoring."""

    S3A = Step3AIntervals()
    S3C = Step3CIntervals()
    S4 = Step4Intervals()
