from django import forms
from django.forms import ModelForm

from publication.models import Publication


class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        fields = ["publication_type", "doi", "pubmed_id"]
        widgets = {
            "publication_type": forms.RadioSelect(),
        }
