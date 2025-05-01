"""Provide the home view for the HCI."""

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """View the home page of the HCI.

    The home page can be thought of as the main hub of the HCI. It is where the user can
    view their curations and their affiliation's curations. It also has links to the
    other pages of the HCI.

    Returns:
        The rendered home page.
    """
    if request.user.is_authenticated and isinstance(request.user, User):
        context = {
            "is_authenticated": True,
            "email": request.user.email,
            "affiliation": "HLA Expert Panel",
            "first_name": request.user.first_name,
        }
    else:
        context = {
            "is_authenticated": False,
        }
    return render(request, "home/index.html", context)
