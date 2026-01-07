"""Houses forms for the auth_ app."""

from django import forms


class PHIForm(forms.Form):
    """Allows the user to sign the PHI agreement."""

    agree = forms.CheckboxInput()
