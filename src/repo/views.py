"""Provides views for the repo app."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def repo_home(request: HttpRequest) -> HttpResponse:
    """Returns the HLARepo's home page."""
    return render(request, "repo/home.html")
