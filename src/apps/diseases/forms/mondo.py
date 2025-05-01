"""Provide a form for adding a disease to the database."""

from django.forms import ModelForm

from apps.diseases.models.mondo import Mondo


class MondoDiseaseForm(ModelForm):
    """Add a Mondo disease to the database."""

    class Meta:
        """Define metadata options."""

        model = Mondo
        fields = ["mondo_id"]
