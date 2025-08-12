"""Houses validation code used in the views module of the curation app."""

from decimal import Decimal, InvalidOperation

from curation.constants.models.evidence import EffectSizeStatistic
from curation.forms import EvidenceEditForm


def validate_effect_size_statistic(form: EvidenceEditForm) -> None:
    """Makes sure there is only one effect size statistic."""
    effect_size_statistic = form.cleaned_data["effect_size_statistic"]
    if effect_size_statistic == EffectSizeStatistic.ODDS_RATIO:
        form.instance.relative_risk_string = ""
        form.instance.relative_risk = None
        form.instance.beta_string = ""
        form.instance.beta = None
    elif effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK:
        form.instance.odds_ratio_string = ""
        form.instance.odds_ratio = None
        form.instance.beta_string = ""
        form.instance.beta = None
    elif effect_size_statistic == EffectSizeStatistic.BETA:
        form.instance.relative_risk_string = ""
        form.instance.relative_risk = None
        form.instance.odds_ratio_string = ""
        form.instance.odds_ratio = None


def maybe_to_decimal(value: str) -> Decimal | None:
    """Tries to convert the value to a Decimal.

    Returns:
         Either a Decimal or None if the conversion fails.
    """
    try:
        decimal_value = Decimal(value)
    except InvalidOperation:
        decimal_value = None
    return decimal_value


def validate_p_value(form: EvidenceEditForm) -> None:
    """Sets the p-value."""
    p_value_string = form.cleaned_data["p_value_string"]
    form.instance.p_value = maybe_to_decimal(p_value_string)


def validate_odds_ratio(form: EvidenceEditForm) -> None:
    """Sets the odds ratio."""
    odds_ratio_string = form.cleaned_data["odds_ratio_string"]
    form.instance.odds_ratio = maybe_to_decimal(odds_ratio_string)


def validate_relative_risk(form: EvidenceEditForm) -> None:
    """Sets the relative risk."""
    relative_risk_string = form.cleaned_data["relative_risk_string"]
    form.instance.relative_risk = maybe_to_decimal(relative_risk_string)


def validate_beta(form: EvidenceEditForm) -> None:
    """Sets the beta coefficient."""
    beta_string = form.cleaned_data["beta_string"]
    form.instance.beta = maybe_to_decimal(beta_string)


def validate_ci_start(form: EvidenceEditForm) -> None:
    """Sets the start of the confidence interval."""
    ci_start_string = form.cleaned_data["ci_start_string"]
    form.instance.ci_start = maybe_to_decimal(ci_start_string)


def validate_ci_end(form: EvidenceEditForm) -> None:
    """Sets the end of the confidence interval."""
    ci_end_string = form.cleaned_data["ci_end_string"]
    form.instance.ci_end = maybe_to_decimal(ci_end_string)
