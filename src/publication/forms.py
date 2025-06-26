"""Provides forms for the publication app."""

from django import forms
from django.forms import ModelForm

from publication.models import Publication


class PublicationForm(ModelForm):
    """Allows the user to add a publication."""

    class Meta:
        """Provides metadata."""

        model = Publication
        fields = ["publication_type", "doi", "pubmed_id"]
        widgets = {
            "publication_type": forms.RadioSelect(),
        }
