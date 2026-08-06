"""Houses code for validating the Curation model's fields."""

from django.core.exceptions import ValidationError

from curation.constants.models.common import Status
from curation.constants.models.curation import CurationTypes


def validate_status(curation) -> None:
    """Blocks submit-for-review if included evidence is still in progress.

    Raises:
        ValidationError: If curation is being submitted for review but has
                         included evidence that is still in progress.
    """
    if curation.status == Status.READY_FOR_REVIEW:
        for evidence in curation.evidence.all():
            if evidence.status == Status.IN_PROGRESS and evidence.is_included:
                raise ValidationError(
                    {"status": "All included evidence must be marked as done."}
                )


def validate_curation_type(curation) -> None:
    """Makes sure the curation has either an allele or a haplotype.

    Raises:
        ValidationError: If an allele curation doesn't have an allele, or a haplotype
                         curation doesn't have a haplotype.
    """
    if curation.curation_type == CurationTypes.ALLELE and curation.allele is None:
        raise ValidationError(
            {"allele": "An allele is required for an allele curation."}
        )
    if curation.curation_type == CurationTypes.HAPLOTYPE and curation.haplotype is None:
        raise ValidationError(
            {"haplotype": "A haplotype is required for a haplotype curation."}
        )
    if curation.curation_type == CurationTypes.ALLELE and curation.haplotype:
        curation.haplotype = None
    if curation.curation_type == CurationTypes.HAPLOTYPE and curation.allele:
        curation.allele = None
