import re
from collections.abc import Callable
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm, modelformset_factory
from django.http import QueryDict
from django.utils import timezone

from allele.models import Allele
from curation.constants.models.curation import (
    CLASSIFICATION_CHOICES,
    TASKFORCE_CHOICES,
    CurationTypes,
)
from curation.models import Curation, Evidence
from disease.models import Disease
from haplotype.models import Haplotype


class CurationCreateForm(ModelForm):
    allele = Allele.name.field.formfield(label="Allele", required=False)
    haplotype = Haplotype.name.field.formfield(label="Haplotype", required=False)
    disease = Disease.mondo_id.field.formfield(label="Disease")
    confirm_duplicate = forms.BooleanField(
        label="Create another curation for this pair anyway",
        required=False,
    )

    class Meta:
        model = Curation
        fields = ["curation_type"]
        widgets = {"curation_type": forms.RadioSelect}

    def __init__(self, *args, **kwargs) -> None:
        """Starts with no existing curations of the pair; clean() finds them."""
        super().__init__(*args, **kwargs)
        self.existing_pairs: list[Curation] = []
        self.haplotype_alleles: list[Allele] = []

    @property
    def can_confirm_duplicate(self) -> bool:
        """Whether the curator may confirm creating a second curation."""
        return len(self.existing_pairs) == 1 and bool(
            self.existing_pairs[0].evidence_count  # ty: ignore[unresolved-attribute]
        )

    def _get_or_build[T](
        self, field: str, get_or_build: Callable[[str], T]
    ) -> T | None:
        """Returns the typed record, existing or unsaved, or reports why it can't.

        Args:
            field: The name of the form field with the typed value.
            get_or_build: The model's get_or_build class method.

        Returns:
            The record, or None if the field is empty or has an error.
        """
        value = self.cleaned_data.get(field)
        if not value:
            return None
        try:
            return get_or_build(value)
        except ValidationError as error:
            self.add_error(field, error.messages)
            return None

    def clean(self) -> dict | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        curation_type = cleaned_data.get("curation_type", "")
        allele = None
        if curation_type == CurationTypes.ALLELE:
            allele = self._get_or_build("allele", Allele.get_or_build)
            self.instance.allele = allele
        haplotype = None
        if curation_type == CurationTypes.HAPLOTYPE:
            result = self._get_or_build("haplotype", Haplotype.get_or_build)
            haplotype, self.haplotype_alleles = result or (None, [])
            self.instance.haplotype = haplotype
        disease = self._get_or_build("disease", Disease.get_or_build)
        if disease:
            self.instance.disease = disease
        # A missing allele or haplotype is reported by Curation.clean(), and a new
        # record has no curations yet.
        target = allele or haplotype
        if not disease or not target or disease.pk is None or target.pk is None:
            return cleaned_data
        self.existing_pairs = list(
            Curation.existing_pairs(
                curation_type=curation_type,
                allele=allele,
                haplotype=haplotype,
                disease=disease,
            )
        )
        # The working group allows one curation for risk evidence and one for
        # protective evidence, so a pair can have at most two.
        if len(self.existing_pairs) >= 2:
            slugs = ", ".join(c.slug for c in self.existing_pairs)
            self.add_error(
                None,
                f"This pair already has two curations ({slugs}). "
                "Add evidence to one of them instead.",
            )
        elif self.existing_pairs and not self.can_confirm_duplicate:
            self.add_error(
                None,
                f"This pair is already being curated in {self.existing_pairs[0].slug}, "
                "which has no evidence yet. Add evidence to it instead.",
            )
        elif self.existing_pairs and not cleaned_data.get("confirm_duplicate"):
            self.add_error(
                None,
                f"This pair is already being curated in {self.existing_pairs[0].slug}. "
                "Review it, then confirm below to create a second curation, for "
                "example for evidence in the opposite direction.",
            )
        return cleaned_data

    def save(self, *args, **kwargs) -> Curation:
        """Saves any new allele, haplotype, or disease with the curation, all or none.

        Returns:
            The curation.
        """
        haplotype = self.instance.haplotype
        new_haplotype = haplotype is not None and haplotype.pk is None
        records = [*self.haplotype_alleles, haplotype]
        records += [self.instance.allele, self.instance.disease]
        with transaction.atomic():
            for record in records:
                if record is not None and record.pk is None:
                    record.added_by = self.instance.added_by
                    record.save()
            if new_haplotype:
                haplotype.alleles.add(*self.haplotype_alleles)
            return super().save(*args, **kwargs)


class TaskforceReviewForm(forms.Form):
    DECISION_CHOICES = [
        ("needs_revision", "Needs Revision"),
        ("approved", "Approved"),
    ]
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect,
    )
    taskforce_classification = forms.ChoiceField(
        label="Classification",
        choices=[("", "---------"), *CLASSIFICATION_CHOICES.items()],
        required=False,
    )
    taskforce_override_reason = forms.CharField(
        label="Suggested Classification Override Reason",
        help_text=(
            "Explain why the taskforce chose a classification other than the "
            "suggested one."
        ),
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}),
        required=False,
    )
    taskforce_evidence_summary = forms.CharField(
        label="Evidence Summary",
        help_text="Replace the bracketed text and remove the parts that don't apply.",
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 16}),
        required=False,
    )
    taskforce_additional_notes = forms.CharField(
        label="Additional Notes",
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}),
        required=False,
    )
    taskforce = forms.ChoiceField(
        label="Taskforce",
        choices=TASKFORCE_CHOICES,
        required=False,
    )
    taskforce_review_date = forms.DateField(
        label="Review Date",
        help_text="The date the taskforce reviewed the curation.",
        required=False,
    )

    def __init__(
        self,
        data: QueryDict | None = None,
        *,
        suggested_classification: str | None = None,
        evidence_summary_template: str = "",
        initial: dict[str, object] | None = None,
    ) -> None:
        """Labels the classification select with the suggested classification.

        Args:
            data: The submitted form data, if any.
            suggested_classification: The curation's suggested classification code.
            evidence_summary_template: The pre-filled evidence summary, which can't
                be approved unchanged.
            initial: Initial values for an unbound form.
        """
        super().__init__(data, initial=initial)
        self.suggested_classification = suggested_classification
        self.evidence_summary_template = evidence_summary_template
        if suggested_classification:
            label = CLASSIFICATION_CHOICES[suggested_classification]
            self.fields[
                "taskforce_classification"
            ].label = f"Classification (suggested: {label})"
        else:
            self.fields[
                "taskforce_classification"
            ].label = "Classification (no suggestion)"

    def clean(self) -> dict | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        decision = cleaned_data.get("decision")
        review_date = cleaned_data.get("taskforce_review_date")
        # TIME_ZONE is UTC, so this is today's date with or without USE_TZ.
        if review_date and review_date > timezone.now().date():
            self.add_error(
                "taskforce_review_date", "The review date can't be in the future."
            )
        self._clean_evidence_summary(cleaned_data, decision)
        evidence_summary = cleaned_data.get("taskforce_evidence_summary")
        if (
            decision == "approved"
            and review_date
            and evidence_summary
            and not _mentions_date(evidence_summary, review_date)
        ):
            # The summary repeats the approval date, so keep it in step with the field.
            self.add_error(
                "taskforce_evidence_summary",
                "Include the review date, "
                f"{review_date:%B} {review_date.day}, {review_date.year}, "
                "as the final approval date.",
            )
        if decision == "approved":
            if not cleaned_data.get("taskforce_classification"):
                self.add_error("taskforce_classification", "Required when approving.")
            if not cleaned_data.get("taskforce"):
                self.add_error("taskforce", "Required when approving.")
            if not review_date:
                self.add_error("taskforce_review_date", "Required when approving.")
            classification = cleaned_data.get("taskforce_classification") or None
            if classification == self.suggested_classification:
                # Don't keep a stale reason from an earlier review.
                cleaned_data["taskforce_override_reason"] = ""
            elif classification and not cleaned_data.get("taskforce_override_reason"):
                self.add_error(
                    "taskforce_override_reason",
                    "Explain why the taskforce chose a classification other than the "
                    "suggested one.",
                )
        return cleaned_data

    def _clean_evidence_summary(self, cleaned_data: dict, decision: str | None) -> None:
        """Rejects or discards an evidence summary that is still the template.

        Args:
            cleaned_data: The form's cleaned data, updated in place.
            decision: The reviewer's decision.
        """
        evidence_summary = cleaned_data.get("taskforce_evidence_summary", "")
        # Browsers submit textarea line breaks as CRLF.
        if (
            self.evidence_summary_template
            and evidence_summary.replace("\r\n", "\n") == self.evidence_summary_template
        ):
            # Don't save the untouched template as if it were a summary.
            cleaned_data["taskforce_evidence_summary"] = ""
            if decision == "approved":
                self.add_error(
                    "taskforce_evidence_summary",
                    "Fill in the template before approving.",
                )
        elif decision == "approved" and not evidence_summary:
            self.add_error("taskforce_evidence_summary", "Required when approving.")


def _mentions_date(text: str, review_date: date) -> bool:
    """Returns whether the text spells out the date in a common format.

    Args:
        text: The text to search.
        review_date: The date to look for.

    Returns:
        True if the text contains the date, e.g., "October 13, 2026",
        "13 October 2026", "Oct 13, 2026", "2026-10-13", or "10/13/2026".
    """
    month = rf"(?:{review_date:%B}|{review_date:%b}\.?)"
    pattern = "|".join(
        [
            rf"{month} {review_date.day},? {review_date.year}",
            rf"{review_date.day} {month},? {review_date.year}",
            review_date.isoformat(),
            f"0?{review_date.month}/0?{review_date.day}/{review_date.year}",
        ]
    )
    normalized = " ".join(text.split())
    return bool(re.search(rf"(?<!\w)(?:{pattern})(?!\w)", normalized, re.IGNORECASE))


class EvidenceCreateForm(ModelForm):
    class Meta:
        model = Evidence
        fields = ["publication"]


class EvidenceTopLevelEditForm(ModelForm):
    class Meta:
        model = Evidence
        fields = ["status", "is_included"]
        widgets = {
            "is_included": forms.CheckboxInput(),
        }


EvidenceTopLevelEditFormSet = modelformset_factory(
    Evidence,
    form=EvidenceTopLevelEditForm,
    extra=0,
)


TEXTAREA_ATTRS = {"class": "textarea", "rows": 2}
YN_BOOL_CHOICES = [(True, "Yes"), (False, "No")]


class EvidenceEditForm(ModelForm):
    class Meta:
        model = Evidence
        fields = [
            "is_gwas",
            "is_gwas_notes",
            "num_fields",
            "num_fields_notes",
            "zygosity",
            "zygosity_notes",
            "phase_confirmed",
            "phase_confirmed_notes",
            "typing_method",
            "typing_method_notes",
            "demographics_text_quotes",
            "demographics",
            "demographics_notes",
            "p_value_string",
            "p_value_notes",
            "multiple_testing_correction",
            "multiple_testing_correction_notes",
            "effect_size_statistic",
            "effect_size_statistic_notes",
            "odds_ratio_string",
            "relative_risk_string",
            "beta_string",
            "ci_start_string",
            "ci_end_string",
            "ci_notes",
            "cohort_size",
            "cohort_size_notes",
            "additional_phenotypes",
            "additional_phenotypes_notes",
            "has_association",
            "has_association_notes",
            "is_protective",
            "is_protective_notes",
            "needs_review",
            "needs_review_notes",
        ]
        widgets = {
            "is_gwas": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "is_gwas_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "num_fields_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "zygosity": forms.RadioSelect,
            "zygosity_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "phase_confirmed": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "phase_confirmed_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "typing_method_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "demographics_text_quotes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "demographics": forms.SelectMultiple,
            "demographics_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "p_value_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "multiple_testing_correction_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "effect_size_statistic_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "ci_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "cohort_size_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "additional_phenotypes_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "has_association": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "has_association_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "is_protective": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "is_protective_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "needs_review": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "needs_review_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
        }

    def clean(self) -> dict | None:
        cleaned_data = super().clean()
        typing_method = cleaned_data.get("typing_method")  # type: ignore
        demographics = cleaned_data.get("demographics")  # type: ignore
        demographics_text_quotes = cleaned_data.get("demographics_text_quotes")  # type: ignore

        # Avoid circular imports.
        from curation.constants.models.evidence import TypingMethod

        if typing_method == TypingMethod.IMPUTATION and not demographics:
            error = "Demographics must be provided if typing method is imputation."
            raise forms.ValidationError({"demographics": error})

        if demographics and not demographics_text_quotes:
            error = "Text quotes must be provided when demographics are entered."
            raise forms.ValidationError({"demographics_text_quotes": error})

        return cleaned_data
