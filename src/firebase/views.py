"""Provides views for the firebase app."""

import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

# The messages below are potentially user-facing.
VERIFICATION_SUCCESS = {
    "valid": True,
    "message": "Verified ID the token from the OAuth provider.",
}
VERIFICATION_FAILURE = {
    "valid": False,
    "message": "Unable to verify the ID token from the OAuth provider.",
}
INVALID_JSON = {
    "valid": False,
    "message": "The JSON sent to the backend to verify the ID token was not valid.",
}


@require_http_methods(["POST"])
def verify(request: HttpRequest) -> JsonResponse:
    """Verifies an ID token obtained from the OAuth provider.

    Args:
         request: The HttpRequest object.

    Returns:
        A JsonResponse object containing a boolean indicating whether the token is
        valid.
    """
    message = VERIFICATION_FAILURE
    try:
        data = json.loads(request.body)
        id_token = data.get("idToken")
        user = authenticate(request, id_token=id_token)
        if user is not None:
            message = VERIFICATION_SUCCESS
            login(request, user, backend="firebase.backends.FirebaseBackend")
    except json.JSONDecodeError:
        message = INVALID_JSON
    return JsonResponse(message)


def login_(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")
    return render(request, "firebase/login.html")


def signup(request: HttpRequest) -> HttpResponse:
    """Returns the signup page."""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")
    return render(request, "firebase/signup.html")
