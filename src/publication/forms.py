from django.forms import ModelForm

from publication.models import Publication


class PublicationForm(ModelForm):
    class Meta:
        model = Publication
        fields = ["pubmed_id"]
        help_texts = {
            "pubmed_id": (
                "The PubMed ID for the publication, e.g., 11910336. Do not use PubMed "
                "IDs of preprint articles, only enter PubMed IDs of peer-reviewed "
                "publications."
            ),
        }
