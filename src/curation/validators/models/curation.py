"""Houses code for validating the Curation model's fields."""

from django.core.exceptions import ValidationError

from curation.constants.models.common import Status
from curation.constants.models.curation import Classification, CurationTypes


def validate_status(curation) -> None:  # noqa: ANN001
    """Makes sure a curation isn't marked done if evidence marked in progress.

    Raises:
        ValidationError: If curation is marked as done but has included evidence
                        that is still in progress.
    """
    if curation.status == Status.DONE:
        for evidence in curation.evidence.all():
            if evidence.status == Status.IN_PROGRESS and evidence.is_included:
                raise ValidationError(
                    {"status": "All included evidence must be marked as done."}
                )


def validate_curation_type(curation) -> None:  # noqa: ANN001
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


def validate_classification(curation) -> None:  # noqa: ANN001
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
