from django.forms import ModelForm

from disease.models import Disease


class DiseaseForm(ModelForm):
    class Meta:
        model = Disease
        fields = ["mondo_id"]
