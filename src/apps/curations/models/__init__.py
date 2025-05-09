"""Ensures DB models for the `curations` app are available at the package level."""

from apps.curations.models.allele.association import (
    AlleleAssociation,
    PubMedAlleleAssociation,
)
from apps.curations.models.allele.curation import AlleleCuration
