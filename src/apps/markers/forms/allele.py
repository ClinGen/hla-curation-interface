"""Provide a form for adding an allele to the database."""

from django.forms import ModelForm

from apps.markers.models.allele import Allele


class AlleleForm(ModelForm):
    """Add an allele to the database."""

    class Meta:
        """Define metadata options."""

        model = Allele
        fields = ["descriptor", "car_id"]
