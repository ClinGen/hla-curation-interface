"""Houses code for validating the Evidence model's fields."""

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from curation.constants.models.evidence import EffectSizeStatistic, TypingMethod


def validate_publication(evidence) -> None:
    """Makes sure the evidence has a publication.

    Raises:
        ValidationError: If the publication is None.
    """
    if evidence.publication is None:
        raise ValidationError({"publication": "Please select a publication."})


def validate_typing_method(evidence) -> None:
    """Makes sure demographics are provided if the typing method is imputation.

    Raises:
        ValidationError: If the user selected imputation as the typing method
                         without providing demographics.
    """
    if (
        evidence.typing_method
        and evidence.typing_method == TypingMethod.IMPUTATION
        and not evidence.demographics.all()
    ):
        message = "Demographics must be provided if typing method is imputation."
        raise ValidationError({"demographics": message})


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


def validate_p_value_string(evidence) -> None:
    """Makes sure the p-value string is valid."""
    message = (
        "Unable to save p-value as written. "
        "Make sure it is written as a decimal (e.g. 0.05) "
        "or in scientific notation (e.g. 5e-8)."
    )
    to_decimal(evidence.p_value_string, "p_value_string", message)


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
