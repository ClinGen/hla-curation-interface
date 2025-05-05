"""Provide a form for adding a curation to the database."""

from django import forms

from apps.curations.models.curation import Curation


class CurationForm(forms.ModelForm):
    """Add more."""

    class Meta:
        """Add more."""

        model = Curation
        fields = ["curation_type", "disease", "allele"]
        widgets = {"curation_type": forms.RadioSelect()}
