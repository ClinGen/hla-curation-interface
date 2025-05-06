"""Provide a form for adding a curation to the database."""

from django import forms

from apps.curations.models.allele import AlleleCuration


class CurationForm(forms.ModelForm):
    """Add more."""

    class Meta:
        """Add more."""

        model = AlleleCuration
        fields = ["disease", "allele"]
