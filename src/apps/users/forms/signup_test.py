"""Test the signup form."""

import pytest

from apps.users.forms.signup import SignupForm


@pytest.mark.component
@pytest.mark.django_db
def test_valid_data() -> None:
    """Make sure the signup form works when given valid data."""
    data = {
        "username": "aketchum",
        "email": "aketchum@kantomail.net",
        "first_name": "Ash",
        "last_name": "Ketchum",
        "password1": "haunter2",
        "password2": "haunter2",
    }
    form = SignupForm(data)
    assert form.is_valid()
    assert form.cleaned_data["username"] == "aketchum"
    assert form.cleaned_data["email"] == "aketchum@kantomail.net"
    assert form.cleaned_data["first_name"] == "Ash"
    assert form.cleaned_data["last_name"] == "Ketchum"
    assert form.cleaned_data["password1"] == "haunter2"
    assert form.cleaned_data["password2"] == "haunter2"
