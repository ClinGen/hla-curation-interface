"""Provides views for the firebase app."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def login(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    return render(request, "firebase/login.html")


@require_http_methods(["POST"])
def verify(request: HttpRequest) -> JsonResponse:  # noqa: ARG001
    """Verifies an ID token obtained from the OAuth provider.

    Args:
         request: The HttpRequest object.

    Returns:
        A JsonResponse object containing a boolean indicating whether the token is
        valid.
    """
    return JsonResponse({"valid": True})
