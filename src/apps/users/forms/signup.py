"""Provide a signup form for first-time users."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from constants import ModelsConstants


class SignupForm(UserCreationForm):
    """Customize the signup form."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(
        max_length=ModelsConstants.MAX_LENGTH_NAME, required=True
    )
    last_name = forms.CharField(
        max_length=ModelsConstants.MAX_LENGTH_NAME, required=True
    )

    class Meta:
        """Define the metadata for the form."""

        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )
