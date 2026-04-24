"""Houses code for validating the Curation model's fields."""

from django.core.exceptions import ValidationError

from curation.constants.models.common import (
    STATUS_CHOICES,
    CurationStatus,
    EvidenceStatus,
)
from curation.constants.models.curation import Classification, CurationTypes

ALLOWED_STATUS_TRANSITIONS = frozenset(
    {
        (CurationStatus.IN_PROGRESS, CurationStatus.PROVISIONAL),
        (CurationStatus.PROVISIONAL, CurationStatus.IN_PROGRESS),
        (CurationStatus.PROVISIONAL, CurationStatus.APPROVED),
        (CurationStatus.APPROVED, CurationStatus.IN_PROGRESS),
        (CurationStatus.APPROVED, CurationStatus.PUBLISHED),
        (CurationStatus.PUBLISHED, CurationStatus.IN_PROGRESS),
    }
)


def validate_status(curation) -> None:
    """Validates the curation's status and any attempted status transition.

    When a curation leaves the in-progress state, every included evidence row
    must be marked as done. When an existing curation's status changes, the
    (from, to) pair must be one of the allowed edges of the workflow state
    machine defined in `ALLOWED_STATUS_TRANSITIONS`.

    Raises:
        ValidationError: If the curation has left the in-progress state but has
                         included evidence that is still in progress, or if the
                         attempted status change is not an allowed transition.
    """
    if curation.status != CurationStatus.IN_PROGRESS:
        for evidence in curation.evidence.all():
            if evidence.status == EvidenceStatus.IN_PROGRESS and evidence.is_included:
                raise ValidationError(
                    {"status": "All included evidence must be marked as done."}
                )

    if not curation.pk:
        return

    previous_status = (
        type(curation)
        .objects.filter(pk=curation.pk)
        .values_list("status", flat=True)
        .first()
    )
    if previous_status is None or previous_status == curation.status:
        return

    if (previous_status, curation.status) not in ALLOWED_STATUS_TRANSITIONS:
        previous_label = STATUS_CHOICES.get(previous_status, previous_status)
        new_label = STATUS_CHOICES.get(curation.status, curation.status)
        raise ValidationError(
            {"status": f"Cannot transition from '{previous_label}' to '{new_label}'."}
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


def validate_classification(curation) -> None:
    """Makes sure the classification is correct for the score.

    Raises:
        ValidationError: If the classification isn't correct for the score.
    """
    if not curation.pk:
        return

    score = curation.score

    if curation.classification == Classification.NO_KNOWN and score != 0:
        raise ValidationError({"classification": "Score must be 0."})

    if curation.classification == Classification.LIMITED and score >= 25:
        raise ValidationError({"classification": "Score must be less than 25."})

    if curation.classification == Classification.MODERATE and not (25 <= score <= 50):
        raise ValidationError({"classification": "Score must be in 25-50."})

    if curation.classification == Classification.STRONG and score < 50:
        raise ValidationError({"classification": "Score must be greater than 50."})

    if curation.classification == Classification.DEFINITIVE and score < 50:
        raise ValidationError({"classification": "Score must be greater than 50."})
