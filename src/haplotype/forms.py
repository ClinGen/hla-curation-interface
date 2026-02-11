from django import forms
from django.forms import ModelForm

from haplotype.models import Haplotype


class HaplotypeForm(ModelForm):
    class Meta:
        model = Haplotype
        fields = ["alleles"]
        widgets = {"alleles": forms.SelectMultiple}
