"""Provide a form for adding a PubMed article to the database."""

from django.forms import ModelForm

from apps.publications.models.pubmed import PubMedArticle


class PubMedArticleForm(ModelForm):
    """Add a PubMed article to the database."""

    class Meta:
        """Define metadata options."""

        model = PubMedArticle
        fields = ["pubmed_id"]
