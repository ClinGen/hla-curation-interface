"""Provides views for the core app."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Returns the home page."""
    messages.debug(request, "Test")
    messages.info(request, "Test")
    messages.success(request, "Test")
    messages.warning(request, "Test")
    messages.error(request, "Test")
    return render(request, "core/home.html")


def about(request: HttpRequest) -> HttpResponse:
    """Returns the about page."""
    return render(request, "core/about.html")


def contact(request: HttpRequest) -> HttpResponse:
    """Returns the contact page."""
    return render(request, "core/contact.html")


def help_(request: HttpRequest) -> HttpResponse:
    """Returns the help page."""
    return render(request, "core/help.html")


def downloads(request: HttpRequest) -> HttpResponse:
    """Returns the downloads page."""
    return render(request, "core/downloads.html")


def citing(request: HttpRequest) -> HttpResponse:
    """Returns the citing page."""
    return render(request, "core/citing.html")


def acknowledgements(request: HttpRequest) -> HttpResponse:
    """Returns the acknowledgements page."""
    return render(request, "core/acknowledgements.html")


def collaborators(request: HttpRequest) -> HttpResponse:
    """Returns the collaborators page."""
    return render(request, "core/collaborators.html")
