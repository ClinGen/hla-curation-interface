"""Provide a form for step 2."""

from django import forms

from apps.curations.models.step_2 import Step2


class Step2Form(forms.ModelForm):
    """Define the form for step 2."""

    class Meta:
        """Define the metadata options."""

        model = Step2
        fields = ["step_2_typing_method"]
