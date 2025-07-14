"""Houses code related to scoring evidence."""


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
    S2_TAG_SNPS_OR_MICROARRAYS = 0
    S2_SEROLOGICAL = 1
    S2_IMPUTATION = 2
    S2_LOW_RES_TYPING = 3
    S2_HIGH_RES_TYPING = 3
    S2_WHOLE_EXOME_SEQ = 3
    S2_SANGER_SEQ = 4
    S2_WHOLE_GENE_SEQ = 4
    S2_WHOLE_GENOME_SEQ_AND_OR_NGS = 5
    S3A_INTERVAL_1 = 0
    S3A_INTERVAL_2 = 0.5
    S3A_INTERVAL_3 = 1
    S3A_INTERVAL_4 = 1.5
    S3A_INTERVAL_5 = 2
    S3B_OVERALL_CORRECTION = 1
    S3B_2_STEP_CORRECTION = 2
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


class Interval:
    """Defines an interval."""

    def __init__(
        self,
        *,
        start: float,
        end: float,
        start_inclusive: bool,
        end_inclusive: bool,
    ) -> None:
        """Sets the interval's start, end, and text representation."""
        self.start = start
        self.end = end
        self.start_inclusive = start_inclusive
        self.end_inclusive = end_inclusive

    def __str__(self) -> str:
        """Returns a string representation of the Interval object for the user."""
        start_operator = "≤" if self.start_inclusive else "<"
        end_operator = "≤" if self.end_inclusive else "<"

        if self.start == float("inf"):
            start = "∞"
        elif self.start == float("-inf"):
            start = "-∞"
        else:
            start = self.start

        if self.end == float("inf"):
            end = "∞"
        elif self.end == float("-inf"):
            end = "-∞"
        else:
            end = self.end

        return f"{start} {start_operator} p-value {end_operator} {end}"

    def __repr__(self) -> str:
        """Returns a string representation of the Interval object for the developer."""
        start_bracket = "[" if self.start_inclusive else "("
        end_bracket = "]" if self.end_inclusive else ")"
        return f"Interval({start_bracket}{self.start}, {self.end}{end_bracket})"

    def contains(self, number: float) -> bool:
        """Returns whether the given number falls within the interval."""
        if self.start_inclusive:
            lower_bound_check = number >= self.start
        else:
            lower_bound_check = number > self.start

        if self.end_inclusive:
            upper_bound_check = number <= self.end
        else:
            upper_bound_check = number < self.end

        return lower_bound_check and upper_bound_check


step_3a_gwas_interval_1 = Interval(
    start=1 * 10e-5,
    end=float("inf"),
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_gwas_interval_2 = Interval(
    start=5 * 10e-8,
    end=step_3a_gwas_interval_1.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_gwas_interval_3 = Interval(
    start=1 * 10e-11,
    end=step_3a_gwas_interval_2.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_gwas_interval_4 = Interval(
    start=1 * 10e-14,
    end=step_3a_gwas_interval_3.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_gwas_interval_5 = Interval(
    start=float("-inf"),
    end=step_3a_gwas_interval_4.start,
    start_inclusive=False,
    end_inclusive=False,
)

step_3a_non_gwas_interval_1 = Interval(
    start=0.05,
    end=float("inf"),
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_non_gwas_interval_2 = Interval(
    start=0.01,
    end=step_3a_non_gwas_interval_1.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_non_gwas_interval_3 = Interval(
    start=0.0005,
    end=step_3a_non_gwas_interval_2.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_non_gwas_interval_4 = Interval(
    start=0.0001,
    end=step_3a_non_gwas_interval_3.start,
    start_inclusive=True,
    end_inclusive=False,
)
step_3a_non_gwas_interval_5 = Interval(
    start=float("-inf"),
    end=step_3a_non_gwas_interval_4.start,
    start_inclusive=False,
    end_inclusive=False,
)

# This is used to render the score table.
FRAMEWORK = [
    {
        "text": "Step 1A: Allele or Haplotype",
        "category": "Allele",
        "split": False,
        "score": "score_step_1a",
        "points": Points.S1A_ALLELE,
    },
    {
        "text": None,
        "category": "Haplotype",
        "split": False,
        "score": "score_step_1a",
        "points": Points.S1A_HAPLOTYPE,
    },
    {
        "text": "Step 1B: Allele Resolution",
        "category": "1-field (see Step 6B)",
        "split": False,
        "score": "score_step_1b",
        "points": Points.S1B_1_FIELD,
    },
    {
        "text": None,
        "category": "2-field",
        "split": False,
        "score": "score_step_1b",
        "points": Points.S1B_2_FIELD,
    },
    {
        "text": None,
        "category": "3-field, G-group, P-group",
        "split": False,
        "score": "score_step_1b",
        "points": Points.S1B_3_FIELD,
    },
    {
        "text": None,
        "category": "4-field",
        "split": False,
        "score": "score_step_1b",
        "points": Points.S1B_4_FIELD,
    },
    {
        "text": "Step 1C: Zygosity",
        "category": "Monoallelic (heterozygous)",
        "split": False,
        "score": "score_step_1c",
        "points": Points.S1C_MONOALLELIC,
    },
    {
        "text": None,
        "category": "Biallelic (homozygous)",
        "split": False,
        "score": "score_step_1c",
        "points": Points.S1C_BIALLELIC,
    },
    {
        "text": "Step 1D: Phase",
        "category": "Phase confirmed",
        "split": False,
        "score": "score_step_1d",
        "points": Points.S1D_PHASE_CONFIRMED,
    },
    {
        "text": "Step 2: Typing Method",
        "category": "Tag SNPs or Microarrays",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_TAG_SNPS_OR_MICROARRAYS,
    },
    {
        "text": None,
        "category": "Serological",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_SEROLOGICAL,
    },
    {
        "text": None,
        "category": "Imputation",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_IMPUTATION,
    },
    {
        "text": None,
        "category": "Low Resolution Typing",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_LOW_RES_TYPING,
    },
    {
        "text": None,
        "category": "High Resolution Typing",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_HIGH_RES_TYPING,
    },
    {
        "text": None,
        "category": "Whole Exome Sequencing",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_WHOLE_EXOME_SEQ,
    },
    {
        "text": None,
        "category": "Sanger-Sequencing-Based Typing",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_SANGER_SEQ,
    },
    {
        "text": None,
        "category": "Whole Gene Sequencing",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_WHOLE_GENE_SEQ,
    },
    {
        "text": None,
        "category": "Whole Genome Sequencing and/or Panel-Based NGS (>50x coverage)",
        "split": False,
        "score": "score_step_2",
        "points": Points.S2_WHOLE_GENOME_SEQ_AND_OR_NGS,
    },
    {
        "text": "Step 3A: Statistics (p-value)",
        "category": ["GWAS", "Non-GWAS"],
        "split": True,
        "score": "score_step_3a",
        "points": "",
    },
    {
        "text": None,
        "category": [step_3a_gwas_interval_1, step_3a_non_gwas_interval_1],
        "split": True,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_1,
    },
    {
        "text": None,
        "category": [step_3a_gwas_interval_2, step_3a_non_gwas_interval_2],
        "split": True,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_2,
    },
    {
        "text": None,
        "category": [step_3a_gwas_interval_3, step_3a_non_gwas_interval_3],
        "split": True,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_3,
    },
    {
        "text": None,
        "category": [step_3a_gwas_interval_4, step_3a_non_gwas_interval_4],
        "split": True,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_4,
    },
    {
        "text": None,
        "category": [step_3a_gwas_interval_5, step_3a_non_gwas_interval_5],
        "split": True,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_5,
    },
    {
        "text": "Step 3B: Multiple Testing Correction",
        "category": "Overall correction for multiple testing",
        "split": False,
        "score": "score_step_3b",
        "points": Points.S3B_OVERALL_CORRECTION,
    },
    {
        "text": None,
        "category": "2-step p-value correction",
        "split": False,
        "score": "score_step_3b",
        "points": Points.S3B_2_STEP_CORRECTION,
    },
    {
        "text": "Step 4: Cohort Size",
        "category": ["GWAS", "Non-GWAS"],
        "split": True,
        "score": "score_step_4",
        "points": "",
    },
    {
        "text": None,
        "category": ["<1,000", "<50"],
        "split": True,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_1,
    },
    {
        "text": None,
        "category": ["1,000-2,499", "50-99"],
        "split": True,
        "score": "score_step_4",
        "points": Points.S3A_INTERVAL_2,
    },
]
