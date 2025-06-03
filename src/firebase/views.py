"""Provides views for the firebase app."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def login(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    return render(request, "firebase/login.html")
