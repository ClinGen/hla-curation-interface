"""Provides views for the firebase app."""

import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.crud import read_user_profile
from firebase.constants.views import (
    INVALID_JSON,
    VERIFICATION_FAILURE,
    VERIFICATION_SUCCESS,
)


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
    return render(request, "firebase/signup.html")


def login_(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    if request.user.is_authenticated:
        messages.info(request, "Already logged in.")
        return redirect("home")
    return render(request, "firebase/login.html")


def logout_(request: HttpRequest) -> HttpResponse:
    """Returns the home page after logging the user out."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Logged out.")
        return redirect("home")
    messages.info(request, "Already logged out.")
    return redirect("home")


def view_profile(request: HttpRequest) -> HttpResponse:
    """Returns the view profile page for the user."""
    if request.user.is_authenticated:
        read = read_user_profile(request.user.username)
        if read is None:
            messages.error(request, "Oops, something is wrong with your profile.")
            return redirect("home")
        user_profile, _ = read
        context = {"user_profile": user_profile}
        return render(request, "firebase/profile_view.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")


def edit_profile(request: HttpRequest) -> HttpResponse:
    """Returns the edit profile page for the user."""
    if request.user.is_authenticated:
        read = read_user_profile(request.user.username)
        if read is None:
            messages.error(request, "Oops, something is wrong with your profile.")
            return redirect("home")
        user_profile, _ = read
        context = {"user_profile": user_profile}
        return render(request, "firebase/profile_edit.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")
