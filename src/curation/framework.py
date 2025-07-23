"""Houses code related to the HLA scoring framework."""

from decimal import Decimal

from curation.interval import Interval


class Points:
    """Defines the points for the steps."""

    S1A_ALLELE = 0
    S1A_HAPLOTYPE = 2
    S1B_1_FIELD = 0
    S1B_2_FIELD = 1
    S1B_3_FIELD = 2
    S1B_4_FIELD = 3
    S1C_MONOALLELIC = 0
    S1C_BIALLELIC = 0.5
    S1D_PHASE_NOT_CONFIRMED = 0
    S1D_PHASE_CONFIRMED = 0.5
    S2_TAG_SNPS = 0
    S2_MICROARRAYS = 0
    S2_SEROLOGICAL = 1
    S2_IMPUTATION = 2
    S2_LOW_RES_TYPING = 3
    S2_HIGH_RES_TYPING = 3
    S2_WHOLE_EXOME_SEQ = 3
    S2_RNA_SEQ = 3
    S2_SANGER_SEQ = 4
    S2_WHOLE_GENE_SEQ = 4
    S2_WHOLE_GENOME_SEQ = 5
    S2_NEXT_GENERATION_SEQ = 5
    S2_LONG_READ_SEQ = 5
    S3A_INTERVAL_1 = 0
    S3A_INTERVAL_2 = 0.5
    S3A_INTERVAL_3 = 1
    S3A_INTERVAL_4 = 1.5
    S3A_INTERVAL_5 = 2
    S3B_OVERALL = 1
    S3B_TWO_STEP = 2
    S3C_OR_RR_BETA = 1
    S3C_CI_DOES_NOT_CROSS = 1
    S4_INTERVAL_1 = 0
    S4_INTERVAL_2 = 1
    S4_INTERVAL_3 = 2
    S4_INTERVAL_4 = 3
    S4_INTERVAL_5 = 4
    S5_SPECIFIC_PHENOTYPE = 2
    S5_ONLY_DISEASE_TESTED = 0
    S6A_ASSOCIATION = 1
    S6A_NO_ASSOCIATION = 0
    S6B_1_FIELD = 0.5
    S6B_MORE_THAN_1_FIELD = 1


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


# This is used to render the evidence score table.
FRAMEWORK = [
    {
        "text": "Step 1A: Allele or Haplotype",
        "category": "Allele",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1a",
        "points": Points.S1A_ALLELE,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Haplotype",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1a",
        "points": Points.S1A_HAPLOTYPE,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 1B: Allele Resolution",
        "category": "1-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_1_FIELD,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 4,
    },
    {
        "text": None,
        "category": "2-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_2_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": "3-field, G-group, P-group",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_3_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": "4-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_4_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 1C: Zygosity",
        "category": "Monoallelic (heterozygous)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1c",
        "points": Points.S1C_MONOALLELIC,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Biallelic (homozygous)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1c",
        "points": Points.S1C_BIALLELIC,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 1D: Phase",
        "category": "Phase confirmed",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1d",
        "points": Points.S1D_PHASE_CONFIRMED,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 1,
    },
    {
        "text": "Step 2: Typing Method",
        "category": "Tagging / Tag SNPs / Microarrays",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_TAG_SNPS,
        "operator": "+",
        "style": "white",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": "Serological",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_SEROLOGICAL,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Imputation",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_IMPUTATION,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Molecular genotyping (low and high resolution) / Whole exome sequencing / RNA sequencing ",  # noqa: E501
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_LOW_RES_TYPING,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Sanger-sequencing-based typing / Whole gene sequencing",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_SANGER_SEQ,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Whole genome sequencing / Panel-based next generation sequencing (> 50x coverage) / Long-read sequencing",  # noqa: E501
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_WHOLE_GENOME_SEQ,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 3A: Statistics (p-value)",
        "category": ["GWAS", "Non-GWAS"],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": "",
        "operator": "",
        "style": "whitesmoke",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_1, Intervals.S3A.NON_GWAS_1],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_1,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_2, Intervals.S3A.NON_GWAS_2],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_2,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_3, Intervals.S3A.NON_GWAS_3],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_3,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_4, Intervals.S3A.NON_GWAS_4],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_4,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_5, Intervals.S3A.NON_GWAS_5],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_5,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 3B: Multiple Testing Correction",
        "category": "Overall correction for multiple testing",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3b",
        "points": Points.S3B_OVERALL,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "2-step p-value correction",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3b",
        "points": Points.S3B_TWO_STEP,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 3C: Statistics (Effect Size)*",
        "category": [
            Intervals.S3C.OR_RR_1,
            Intervals.S3C.OR_RR_2,
            Intervals.S3C.BETA_1,
            Intervals.S3C.BETA_2,
        ],
        "split_horizontal": False,
        "split_vertical": True,
        "score": "score_step_3c1",
        "points": Points.S3C_OR_RR_BETA,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "CI does not cross 1 (OR/RR) or 0 (beta)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3c2",
        "points": Points.S3C_CI_DOES_NOT_CROSS,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 4: Cohort Size",
        "category": ["GWAS", "Non-GWAS"],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": "",
        "operator": "",
        "style": "white",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_1, Intervals.S4.NON_GWAS_1],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_1,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_2, Intervals.S4.NON_GWAS_2],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_2,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_3, Intervals.S4.NON_GWAS_3],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_3,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_4, Intervals.S4.NON_GWAS_4],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_4,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_5, Intervals.S4.NON_GWAS_5],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_5,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 5: Additional Phenotypes",
        "category": "Has specific disease-related phenotype",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_5",
        "points": Points.S5_SPECIFIC_PHENOTYPE,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Only disease tested",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_5",
        "points": Points.S5_ONLY_DISEASE_TESTED,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "is_total_row": True,
        "score": "score_before_multipliers",
        "text": "Total Before Multipliers",
        "style": "lightblue",
        "id": "total-score-before-multipliers",
    },
    {
        "text": "Step 6A: Weighing Association (multiplier)",
        "category": "Significant association with disease",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6a",
        "points": Points.S6A_ASSOCIATION,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "No significant association",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6a",
        "points": Points.S6A_NO_ASSOCIATION,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "white",
    },
    {
        "text": "Step 6B: Low Field Resolution (multiplier)",
        "category": "1-field resolution",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6b",
        "points": Points.S6B_1_FIELD,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "> 1-field resolution",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6b",
        "points": Points.S6B_MORE_THAN_1_FIELD,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "whitesmoke",
    },
    {
        "is_total_row": True,
        "score": "score",
        "text": "Total",
        "style": "lightblue",
        "id": "total-score",
    },
]
