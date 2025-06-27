"""Provides forms for the allele app."""

from django.forms import ModelForm

from allele.models import Allele


class AlleleForm(ModelForm):
    """Allows the user to add an allele."""

    class Meta:
        """Provides metadata."""

        model = Allele
        fields = ["car_id"]
