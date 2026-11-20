"""Houses constants used in the models module of the haplotype app."""

import re

# Separates the allele names in a haplotype's stored name, e.g., A*01:01~B*08:01.
HAPLOTYPE_NAME_SEPARATOR = "~"

# Curators may separate the alleles they type with ~, whitespace, or commas.
ALLELE_SEPARATORS = re.compile(r"[~,\s]+")

# Genes on chromosome 6 ordered by location in ascending order.
# See https://hla.alleles.org/pages/genes/genes_map/.
GENE_LIST = [
    "HFE",
    "F",
    "V",
    "P",
    "G",
    "H",
    "T",
    "K",
    "U",
    "A",
    "W",
    "Y",
    "R",
    "J",
    "L",
    "N",
    "E",
    "C",
    "B",
    "S",
    "MICA",
    "MICB",
    "DRA",
    "DRB9",
    "DRB8",
    "DRB7",
    "DRB6",
    "DRB5",
    "DRB4",
    "DRB3",
    "DRB2",
    "DRB1",
    "DQA1",
    "DQB1",
    "DQB3",
    "DQA2",
    "DQB2",
    "DOB",
    "TAP2",
    "TAP1",
    "Z",
    "DMB",
    "DMA",
    "DOA",
    "DPA1",
    "DPB1",
    "DPA2",
    "DPB2",
]
