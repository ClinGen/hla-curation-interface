"""Houses constants used by the Curation model."""


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

HLA_CURATION_TASKFORCE_ID = "40033"

# The expert panels that can review curations, as (ID, name) pairs.
EP_CHOICES = [(HLA_CURATION_TASKFORCE_ID, "HLA Curation Taskforce")]

# Shown when a curation has no EP classification and no suggested one.
NO_CLASSIFICATION_LABEL = "No Classification Set"
