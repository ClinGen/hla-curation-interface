"""Houses validation code for the models module of the disease app."""

from django.core.exceptions import ValidationError

from disease.constants.models import DiseaseTypes


def validate_disease_type(disease) -> None:
    """Makes sure we get the correct ID given the disease type.

    Raises:
        ValidationError: If the ID for the disease isn't provided. For example, a Mondo
                         disease requires a Mondo ID.
    """
    if disease.disease_type == DiseaseTypes.MONDO and not disease.mondo_id:
        raise ValidationError(
            {"mondo_id": "The Mondo ID is required for Mondo disease."}
        )


def validate_mondo_id(disease) -> None:
    """Makes sure the Mondo ID is correct.

    Raises:
        ValidationError: If the Mondo ID doesn't have 'MONDO:' at the beginning.
    """
    if disease.mondo_id and "MONDO:" not in disease.mondo_id[:6]:
        raise ValidationError(
            {"mondo_id": "The prefix 'MONDO:' is required for Mondo IDs."}
        )
