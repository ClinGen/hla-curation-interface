"""Provides a form for adding allele associations to the database.

This form allows curators to create an allele association for the curation they
are working on.
"""

from django import forms

from apps.curations.models.allele.association import PubMedAlleleAssociation


class AlleleAssociationForm(forms.Form):
    """Allows users to select the publication type for their association."""

    PUBLICATION_TYPE_CHOICES = [
        ("pubmed", "PubMed Article"),
        ("biorxiv", "bioRxiv Paper"),
        ("medrxiv", "medRxiv Paper"),
    ]
    publication_type = forms.ChoiceField(choices=PUBLICATION_TYPE_CHOICES)


class PubMedAlleleAssociationForm(forms.ModelForm):
    """Enables users to create or edit the PubMed allele association."""

    class Meta:
        """Configures the fields for the form."""

        model = PubMedAlleleAssociation
        fields = [
            "pubmed_article",
            "is_included_for_scoring",
            "is_conflicting_evidence",
        ]
