"""Houses validation code for the models module of the disease app."""

import re

from django.core.exceptions import ValidationError

from disease.constants.models import DiseaseTypes


def validate_disease_type_mondo(disease) -> None:
    """Makes sure we get a Mondo ID if the disease type is set to Mondo.

    Raises:
        ValidationError: If the Mondo ID for the Mondo disease isn't provided.
    """
    if disease.disease_type == DiseaseTypes.MONDO and not disease.mondo_id:
        raise ValidationError(
            {"mondo_id": "The Mondo ID is required for Mondo disease."}
        )


def validate_mondo_id(disease) -> None:
    """Makes sure the Mondo ID is correct.

    Raises:
        ValidationError: If the Mondo ID doesn't have 'MONDO:' at the beginning,
            or isn't followed by exactly seven digits.
    """
    if not disease.mondo_id:
        return
    if not disease.mondo_id.startswith("MONDO:"):
        raise ValidationError(
            {"mondo_id": "The prefix 'MONDO:' is required for Mondo IDs."}
        )
    if not re.fullmatch(r"MONDO:\d{7}", disease.mondo_id):
        raise ValidationError(
            {
                "mondo_id": (
                    "A Mondo ID is 'MONDO:' followed by seven digits, e.g., "
                    "MONDO:0005052."
                )
            }
        )
