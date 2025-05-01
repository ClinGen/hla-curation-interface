"""Provide a form for step 3."""

from django import forms

from apps.curations.models.step_3 import Step3


class Step3Form(forms.ModelForm):
    """Define the form for step 3."""

    class Meta:
        """Define the metadata options."""

        model = Step3
        fields = ["is_gwas", "significand", "exponent"]
