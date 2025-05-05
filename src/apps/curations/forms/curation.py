"""Provide a form for adding a curation to the database."""

from django import forms

from apps.curations.models.curation import Curation


class CurationForm(forms.ModelForm):
    """Add more."""

    class Meta:
        """Add more."""

        model = Curation
        fields = ["curation_type", "disease", "allele"]

    def __init__(self, *args, **kwargs) -> None:
        """Add more."""
        super().__init__(*args, **kwargs)
        self.fields["curation_type"].widget = forms.RadioSelect(
            choices=[
                ("allele", "Allele Curation"),
                ("haplotype", "Haplotype Curation"),
            ]
        )
        self.fields["curation_type"].label = "Type of Curation"
        self.fields["allele"].queryset = self.fields["allele"].queryset.order_by(
            "descriptor"
        )
        self.fields["disease"].queryset = self.fields["disease"].queryset.order_by(
            "mondo_id"
        )
