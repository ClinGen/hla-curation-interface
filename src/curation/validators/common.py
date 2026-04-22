"""Houses code used in other curation validator modules."""

from decimal import Decimal

from curation.constants.score import Intervals


def has_association_and_p_value_err_msg(
    p_value: Decimal, *, is_gwas: bool, has_association: bool
) -> str | None:
    """Returns an error message if has_association=True and p-value is insignificant.

    Args:
        p_value: The p-value for the evidence.
        is_gwas: Whether the evidence references a genome-wide association study.
        has_association: Whether there is a significant association with the disease.

    Returns:
        An error message if has_association=True and p-value is insignificant (i.e. if
        the p-value is in the first interval in step 3A or if the p-value isn't
        provided).
    """
    if has_association and p_value is None:
        return (
            "No p-value provided. "
            "p-value must be provided to set 'Significant Association' to 'Yes'."
        )
    if has_association and is_gwas and Intervals.S3A.GWAS_1.contains(p_value):
        return (
            f"The p-value ({p_value}) is not significant "
            f"(>= {Intervals.S3A.GWAS_1.start} for GWAS. "
            "Please set 'Significant Association' to 'No'."
        )
    if has_association and not is_gwas and Intervals.S3A.NON_GWAS_1.contains(p_value):
        return (
            f"The p-value ({p_value}) is not significant "
            f"(>= {Intervals.S3A.NON_GWAS_1.start} for non-GWAS. "
            "Please set 'Significant Association' to 'No'."
        )
    return None
