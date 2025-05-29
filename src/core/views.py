"""Provides views for the core app."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Returns the home page."""
    return render(request, "core/home.html")
