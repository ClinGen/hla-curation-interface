"""Provides views for the firebase app."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def sign_in(request: HttpRequest) -> HttpResponse:
    """Returns the sign-in page."""
    return render(request, "firebase/sign_in.html")
