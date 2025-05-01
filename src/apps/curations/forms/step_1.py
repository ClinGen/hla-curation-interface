"""Provide a form for step 1."""

from django import forms

from apps.curations.models.step_1 import Step1


class Step1Form(forms.ModelForm):
    """Define the form for step 1."""

    class Meta:
        """Define the metadata options."""

        model = Step1
        fields = [
            "step_1a_marker_type",
            "step_1b_allele_resolution",
            "step_1c_zygosity",
            "step_1d_phase_is_confirmed",
        ]
