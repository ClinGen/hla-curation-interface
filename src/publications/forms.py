"""Provides forms for the publications app."""

from django import forms
from django.forms import ModelForm

from publications.models import Publication


class PublicationForm(ModelForm):
    """Allows the user to add a publication."""

    class Meta:
        """Provides metadata."""

        model = Publication
        fields = ["publication_type", "doi", "pubmed_id"]
        widgets = {
            "publication_type": forms.RadioSelect(),
        }
