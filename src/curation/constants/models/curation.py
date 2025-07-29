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
