"""Provide a login form."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField


class LoginForm(AuthenticationForm):
    """Customize the login form."""

    username = UsernameField()
    password = forms.CharField(widget=forms.PasswordInput)
