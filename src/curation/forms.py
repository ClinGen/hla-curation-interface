"""Provides forms for the curation app."""

from django import forms
from django.forms import ModelForm

from curation.models import Curation


class CurationForm(ModelForm):
    """Allows the user to add a curation."""

    class Meta:
        """Provides metadata."""

        model = Curation
        fields = ["curation_type", "allele"]
        widgets = {"curation_type": forms.RadioSelect}
