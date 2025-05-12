"""Provides a form for adding PubMed allele associations to the database.

This form allows curators to create a PubMed allele association for the curation they
are working on.
"""

from django import forms

from apps.curations.models.allele.association import PubMedAlleleAssociation
from constants import ModelsConstants


class BasicInfoForm(forms.ModelForm):
    """Collects basic info for the PubMed allele association."""

    class Meta:
        """Configures the fields for the form."""

        model = PubMedAlleleAssociation
        fields = [
            "pubmed_article",
            "is_included_for_scoring",
            "is_conflicting_evidence",
        ]


class ZygosityForm(forms.ModelForm):
    """Collects zygosity info for the PubMed allele association."""

    class Meta:
        """Configures the field for the form."""

        model = PubMedAlleleAssociation
        fields = ["zygosity"]
        widgets = {
            "zygosity": forms.RadioSelect(choices=ModelsConstants.CHOICES_ZYGOSITY)
        }
