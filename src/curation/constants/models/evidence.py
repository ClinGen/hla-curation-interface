"""Houses constants used by the Evidence model."""


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
    TypingMethod.WHOLE_GENE_SEQ: "Whole Gene Sequencing",
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
    AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED: "Has specific disease-related phenotype",  # noqa: E501
    AdditionalPhenotypes.ONLY_DISEASE_TESTED: "Only disease tested",
}
