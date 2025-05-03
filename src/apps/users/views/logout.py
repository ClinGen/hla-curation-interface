"""Provide a logout view."""

from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def custom_logout(request: HttpRequest) -> HttpResponse:
    """Return"""
    logout(request)
    return redirect("home")
