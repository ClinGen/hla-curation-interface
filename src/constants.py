"""Provide constants used in the project.

We organize constants into classes to keep things organized. The classes themselves
should be sorted alphabetically. Within each class, the constants should be sorted
alphabetically.
"""


class AffiliationsConstants:
    """Define constants related to affiliations."""

    DEFAULT_ID = "10119"
    DEFAULT_NAME = "HLA Expert Panel"
    MAX_LENGTH_ID = 5


class CARConstants:
    """Define constants related to the ClinGen Allele Registry."""

    API_URL = "https://reg.genome.network/allele/hla"


class HumanReadableIDPrefixConstants:
    """Define human-readable ID prefixes to be used in the HCI.

    This class should be imported as `HRIDPrefixes`.
    """

    ALLELE_CURATION = "ALC"
    ALLELE_ASSOCIATION = "ALA"
    HAPLOTYPE_CURATION = "HPC"
    HAPLOTYPE_ASSOCIATION = "HPA"


class IPDConstants:
    """Define constants related to IPD-IMGT/HLA database."""

    SEARCH_URL = "https://www.ebi.ac.uk/ipd/imgt/hla/alleles/"


class ModelsConstants:
    """Define constants related to models."""

    CHOICES_ZYGOSITY = [
        ("mo", "Monoallelic (heterozygous)"),
        ("bi", "Biallelic (homozygous)"),
    ]
    CHOICES_TYPING_METHODS = [
        ("tag", "Tag SNPs"),
        ("mic", "Microarrays"),
        ("ser", "Serological"),
        ("imp", "Imputation"),
        ("lrt", "Low Resolution Typing"),
        ("hrt", "High Resolution Typing"),
        ("wes", "Whole Exome Sequencing"),
        ("san", "Sanger Sequencing-Based Typing"),
        ("gen", "Whole Gene Sequencing"),
        ("nom", "Whole Genome Sequencing"),
        ("pbn", "Panel-Based NGS (>50x coverage)"),
        ("nop", "Whole Genome Sequencing and Panel-Based NGS (>50x coverage)"),
    ]
    DECIMAL_PLACES_P_VALUE = 30
    MAX_DIGITS_P_VALUE = 31
    MAX_LENGTH_NAME = 255
    MAX_LENGTH_HUMAN_READABLE_ID = 3
    MAX_LENGTH_TYPING_METHODS = 3
    MAX_LENGTH_ZYGOSITY = 2


class MondoConstants:
    """Define constants related to the Mondo Disease Ontology."""

    API_URL = "https://www.ebi.ac.uk/ols4/api/ontologies/mondo/terms"
    IRI = "http://purl.obolibrary.org/obo"
    SEARCH_URL = "https://www.ebi.ac.uk/ols4/ontologies/mondo"


class PublicationTypeConstants:
    """Define the string values for the publication types."""

    BIORXIV = "biorxiv"
    MEDRXIV = "medrxiv"
    PUBMED = "pubmed"


class PubMedConstants:
    """Define constants related to PubMed."""

    API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    SEARCH_URL = "https://pubmed.ncbi.nlm.nih.gov/"


class RequestsConstants:
    """Define constants related to the requests library."""

    DEFAULT_TIMEOUT = 5  # In seconds.
