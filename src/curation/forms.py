"""Provides forms for the curation app."""

from django import forms
from django.forms import ModelForm, modelformset_factory

from curation.models import Curation, Evidence


class CurationCreateForm(ModelForm):
    """Allows the user to add a curation."""

    class Meta:
        """Provides metadata."""

        model = Curation
        fields = ["curation_type", "allele", "haplotype", "disease"]
        widgets = {"curation_type": forms.RadioSelect}


class CurationEditForm(ModelForm):
    """Allows the user to edit a curation."""

    class Meta:
        """Provides metadata."""

        model = Curation
        fields = ["status", "classification"]


class EvidenceCreateForm(ModelForm):
    """Allows the user to add evidence."""

    class Meta:
        """Provides metadata."""

        model = Evidence
        fields = ["publication"]


class EvidenceTopLevelEditForm(ModelForm):
    """Allows the user to edit the top-level evidence fields."""

    class Meta:
        """Provides metadata."""

        model = Evidence
        fields = ["status", "is_conflicting", "is_included"]
        widgets = {
            "is_conflicting": forms.CheckboxInput(),
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
    """Allows the user to edit all evidence fields other than the top-level fields."""

    class Meta:
        """Provides metadata."""

        model = Evidence
        fields = [
            "is_gwas",
            "is_gwas_notes",
            "zygosity",
            "zygosity_notes",
            "phase_confirmed",
            "phase_confirmed_notes",
            "typing_method",
            "typing_method_notes",
            "p_value_string",
            "p_value_notes",
        ]
        widgets = {
            "is_gwas": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "is_gwas_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "zygosity": forms.RadioSelect(),
            "zygosity_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "phase_confirmed": forms.RadioSelect(choices=YN_BOOL_CHOICES),
            "phase_confirmed_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "typing_method_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
            "p_value_notes": forms.Textarea(attrs=TEXTAREA_ATTRS),
        }
