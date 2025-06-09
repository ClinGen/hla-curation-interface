"""Provides views for the firebase app."""

import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from firebase.clients import get_user_info

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


def signup(request: HttpRequest) -> HttpResponse:
    """Returns the signup page."""
    if request.user.is_authenticated:
        messages.info(request, "Already logged in.")
        return redirect("home")
    return render(request, "firebase/auth/signup.html")


def login_(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    if request.user.is_authenticated:
        messages.info(request, "Already logged in.")
        return redirect("home")
    return render(request, "firebase/auth/login.html")


def logout_(request: HttpRequest) -> HttpResponse:
    """Returns the home page after logging the user out."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Logged out.")
        return redirect("home")
    messages.info(request, "Already logged out.")
    return redirect("home")


def profile_view(request: HttpRequest) -> HttpResponse:
    """Returns the view profile page for the user."""
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.username)
        context = {"user_info": user_info}
        return render(request, "firebase/profile/view.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")


def profile_edit(request: HttpRequest) -> HttpResponse:
    """Returns the edit profile page for the user."""
    if request.user.is_authenticated:
        user_info = get_user_info(request.user.username)
        context = {"user_info": user_info}
        return render(request, "firebase/profile/edit.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")
