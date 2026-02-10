from django.forms import ModelForm

from allele.models import Allele


class AlleleForm(ModelForm):
    class Meta:
        model = Allele
        fields = ["name"]
