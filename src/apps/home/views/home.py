"""Provide the home view for the HCI."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from constants import LogoColorConstants


def home(request: HttpRequest) -> HttpResponse:
    """View the home page of the HCI.

    The home page can be thought of as the main hub of the HCI. It is where the user can
    view their curations and their affiliation's curations. It also has links to the
    other pages of the HCI.

    Returns:
        The rendered home page.
    """
    context = {
        "affiliation": "HLA Expert Panel",
        "hero_bg_color": LogoColorConstants.PURPLE,
        "hero_link_color": LogoColorConstants.ORANGE,
        "hero_text_color": "white",
    }
    return render(request, "home/index.html", context)
