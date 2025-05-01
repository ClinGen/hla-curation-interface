"""Test the signup view."""

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertTemplateUsed


@pytest.fixture
def client() -> Client:
    """Return a Django test client."""
    return Client()


@pytest.mark.integration
def test_get(client: Client) -> None:
    """Test the GET request."""
    url = reverse("signup")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, "HCI Signup")
    assertContains(response, "Username")
    assertContains(response, "Email")
    assertContains(response, "First name")
    assertContains(response, "Last name")
    assertContains(response, "Password")
    assertContains(response, "Sign Up")
    assertContains(response, "Already have an account?")
    assertContains(response, "Log In")
    assertTemplateUsed(response, "users/signup.html")
