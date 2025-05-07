"""Provides a form for adding an allele curation to the database.

This form allows curators to associate a specific HLA allele with a particular disease
at the initial stage of the curation workflow.
"""

from django import forms

from apps.curations.models.allele import AlleleCuration


class AlleleCurationForm(forms.ModelForm):
    """Enables users to select a disease and allele for their curation."""

    class Meta:
        """Configures the fields for the form."""

        model = AlleleCuration
        fields = ["disease", "allele"]
