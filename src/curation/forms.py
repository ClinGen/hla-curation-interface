from django import forms
from django.forms import ModelForm, modelformset_factory

from curation.constants.models.curation import CLASSIFICATION_CHOICES
from curation.models import Curation, Evidence

HLA_CURATION_TASKFORCE_ID = "40033"

EP_CHOICES = [(HLA_CURATION_TASKFORCE_ID, "HLA Curation Taskforce")]


class CurationCreateForm(ModelForm):
    class Meta:
        model = Curation
        fields = ["curation_type", "allele", "haplotype", "disease"]
        widgets = {"curation_type": forms.RadioSelect}


class EPReviewForm(forms.Form):
    DECISION_CHOICES = [
        ("needs_revision", "Needs Revision"),
        ("approved", "Approved"),
    ]
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect,
    )
    ep_classification = forms.ChoiceField(
        label="Classification",
        choices=[("", "---------"), *CLASSIFICATION_CHOICES.items()],
        required=False,
    )
    ep_evidence_summary = forms.CharField(
        label="Evidence Summary",
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}),
        required=False,
    )
    ep_additional_notes = forms.CharField(
        label="Additional Notes",
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}),
        required=False,
    )
    ep = forms.ChoiceField(
        label="Expert Panel",
        choices=EP_CHOICES,
        required=False,
    )

    def clean(self) -> dict | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data
        decision = cleaned_data.get("decision")
        if decision == "approved":
            if not cleaned_data.get("ep_classification"):
                self.add_error("ep_classification", "Required when approving.")
            if not cleaned_data.get("ep_evidence_summary"):
                self.add_error("ep_evidence_summary", "Required when approving.")
            if not cleaned_data.get("ep"):
                self.add_error("ep", "Required when approving.")
        return cleaned_data


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
