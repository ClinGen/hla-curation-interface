"""Provides forms for the haplotype app."""

from django import forms
from django.forms import ModelForm

from haplotype.models import Haplotype


class HaplotypeForm(ModelForm):
    """Allows the user to add a haplotype."""

    class Meta:
        """Provides metadata."""

        model = Haplotype
        fields = ["alleles"]
        widgets = {"alleles": forms.SelectMultiple}
