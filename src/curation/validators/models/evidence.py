"""Houses code for validating the Evidence model's fields."""

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from curation.constants.models.curation import CurationTypes
from curation.constants.models.evidence import EffectSizeStatistic, PValueComparator
from curation.validators.common import has_association_and_p_value_err_msg
from publication.constants.models import PublicationTypes


def _max_num_fields(evidence) -> int | None:
    """Returns the maximum allowed num_fields for the evidence's allele or haplotype."""
    curation = evidence.curation
    if not curation:
        return None
    if curation.curation_type == CurationTypes.ALLELE and curation.allele:
        return curation.allele.name.count(":") + 1
    if curation.curation_type == CurationTypes.HAPLOTYPE and curation.haplotype:
        alleles = curation.haplotype.alleles.all()
        if alleles:
            return min(a.name.count(":") + 1 for a in alleles)
    return None


def validate_num_fields(evidence) -> None:
    """Validates that num_fields does not exceed what the allele or haplotype supports.

    Raises:
        ValidationError: If num_fields is greater than the maximum allowed.
    """
    if evidence.num_fields is None:
        return
    max_fields = _max_num_fields(evidence)
    if max_fields is not None and evidence.num_fields > max_fields:
        raise ValidationError(
            {
                "num_fields": (
                    f"The selected resolution ({evidence.num_fields}-field) exceeds "
                    f"the maximum supported by this allele or haplotype "
                    f"({max_fields}-field)."
                )
            }
        )


def validate_publication(evidence) -> None:
    """Makes sure the evidence has a publication.

    Raises:
        ValidationError: If the publication is None.
    """
    if evidence.publication is None:
        raise ValidationError({"publication": "Please select a publication."})


def validate_preprint_not_included(evidence) -> None:
    """Makes sure preprint publications cannot be included in curations.

    Raises:
        ValidationError: If publication is included and is a preprint.
    """
    if evidence.publication is None:
        return
    preprint_types = (PublicationTypes.BIORXIV, PublicationTypes.MEDRXIV)
    if evidence.is_included and evidence.publication.publication_type in preprint_types:
        raise ValidationError(
            {
                "is_included": (
                    "Preprint publications (bioRxiv and medRxiv) cannot be included "
                    "in curations. Please use a PubMed publication instead."
                )
            }
        )


def to_decimal(string_value: str, field: str, message: str) -> None:
    """Returns the Decimal object for the given string.

    Raises:
        ValidationError: If the string can't be converted to a Decimal object.
    """
    if string_value != "":
        try:
            Decimal(string_value)
        except InvalidOperation as exc:
            raise ValidationError({field: message}) from exc


def parse_p_value_string(p_value_string: str) -> tuple[str, str]:
    """Parses a p-value string into (comparator_code, numeric_string).

    Args:
        p_value_string: The raw p-value string from user input.

    Returns:
        A tuple of (comparator_code, numeric_string).

    Examples:
        "0.05" -> ("", "0.05")
        "< 0.0001" -> ("LT", "0.0001")
        "<=5e-8" -> ("LE", "5e-8")
        "<= 1e-10" -> ("LE", "1e-10")

    Raises:
        ValidationError: If the comparator is unsupported (> or >=).
    """
    string = p_value_string.strip()
    if not string:
        return "", ""

    # Check for <= first (before <).
    if string.startswith("<="):
        return PValueComparator.LESS_THAN_OR_EQUAL, string[2:].strip()
    if string.startswith("<"):
        return PValueComparator.LESS_THAN, string[1:].strip()

    # Reject unsupported comparators.
    if string.startswith((">", ">=")):
        raise ValidationError(
            {
                "p_value_string": (
                    "The > and >= comparators are not supported. "
                    "Please enter an exact value or use < or <=."
                )
            }
        )

    return "", string


def validate_p_value_string(evidence) -> None:
    """Validates the p-value string and parses it onto the instance.

    Raises:
        ValidationError: If the p-value string cannot be parsed into a Decimal.
    """
    message = (
        "Unable to save p-value as written. "
        "Make sure it is written as a decimal (e.g. 0.05), "
        "in scientific notation (e.g. 5e-8), or with a comparator (e.g. < 0.0001)."
    )
    comparator, numeric_part = parse_p_value_string(evidence.p_value_string)
    evidence.p_value_comparator = comparator
    if numeric_part == "":
        evidence.p_value = None
        return
    try:
        evidence.p_value = Decimal(numeric_part)
    except InvalidOperation as exc:
        raise ValidationError({"p_value_string": message}) from exc


def validate_effect_size_statistic(evidence) -> None:
    """Makes sure there is only one effect size statistic."""
    if evidence.effect_size_statistic == EffectSizeStatistic.ODDS_RATIO:
        evidence.relative_risk_string = ""
        evidence.relative_risk = None
        evidence.beta_string = ""
        evidence.beta = None
    elif evidence.effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK:
        evidence.odds_ratio_string = ""
        evidence.odds_ratio = None
        evidence.beta_string = ""
        evidence.beta = None
    elif evidence.beta_string == EffectSizeStatistic.BETA:
        evidence.relative_risk_string = ""
        evidence.relative_risk = None
        evidence.odds_ratio_string = ""
        evidence.odds_ratio = None


def validate_odds_ratio_string(evidence) -> None:
    """Makes sure the odds ratio string is valid."""
    message = (
        "Unable to save odds ratio as written. "
        "Make sure it is written as an integer or decimal."
    )
    to_decimal(evidence.odds_ratio_string, "odds_ratio_string", message)


def validate_relative_risk_string(evidence) -> None:
    """Makes sure the relative risk string is valid."""
    message = (
        "Unable to save relative risk as written. "
        "Make sure it is written as an integer or decimal."
    )
    to_decimal(evidence.relative_risk_string, "relative_risk_string", message)


def validate_beta_string(evidence) -> None:
    """Makes sure the beta string is valid."""
    message = (
        "Unable to save beta coefficient as written. "
        "Make sure it is written as an integer or decimal."
    )
    to_decimal(evidence.beta_string, "beta_string", message)


def validate_ci_start_string(evidence) -> None:
    """Makes sure the CI start string is valid."""
    message = (
        "Unable to save confidence interval start as written. "
        "Make sure it is written as a decimal."
    )
    to_decimal(evidence.ci_start_string, "ci_start_string", message)


def validate_ci_end_string(evidence) -> None:
    """Makes sure the CI end string is valid."""
    message = (
        "Unable to save confidence interval end as written. "
        "Make sure it is written as a decimal."
    )
    to_decimal(evidence.ci_end_string, "ci_end_string", message)


def validate_has_association_and_p_value(evidence) -> None:
    """Validates that has_association is False if p-value is insignificant.

    Args:
        evidence: The model instance.

    Raises:
        ValidationError: If has_association is True but p-value is insignificant.
    """
    err_msg = has_association_and_p_value_err_msg(
        evidence.p_value,
        is_gwas=evidence.is_gwas,
        has_association=evidence.has_association,
    )
    if err_msg:
        raise ValidationError({"has_association": err_msg})
