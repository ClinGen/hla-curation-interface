"""Provides forms for the disease app."""

from django.forms import ModelForm

from disease.models import Disease


class DiseaseForm(ModelForm):
    """Allows the user to add a disease."""

    class Meta:
        """Provides metadata."""

        model = Disease
        fields = ["mondo_id"]
