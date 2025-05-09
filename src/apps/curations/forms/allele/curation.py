"""Provides a form for adding an allele curation to the database.

This form allows curators to create a new curation for an allele-disease pair.
"""

from django import forms

from apps.curations.models.allele.curation import AlleleCuration


class AlleleCurationForm(forms.ModelForm):
    """Enables users to select a disease and allele for their curation."""

    class Meta:
        """Configures the fields for the form."""

        model = AlleleCuration
        fields = ["disease", "allele"]
