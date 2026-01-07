"""Provides views for the auth_ app."""

import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from workos import WorkOSClient

from auth_.forms import PHIForm
from core.models import UserProfile

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
)

cookie_password = os.getenv("WORKOS_COOKIE_PASSWORD")


def login_(request: HttpRequest) -> HttpResponseRedirect:
    """Logs the user in.

    Returns:
        A redirect response that sends the user to WorkOS's hosted login page.
    """
    if request.user.is_authenticated:
        messages.info(request, "Already logged in.")
        return redirect("home")
    authorization_url = workos.user_management.get_authorization_url(
        provider="authkit",
        redirect_uri=os.getenv("WORKOS_REDIRECT_URI"),  # type: ignore
    )
    return redirect(authorization_url)


def callback(request: HttpRequest) -> HttpResponseRedirect:
    """Authenticates the user and redirects them to the home page.

    Returns:
        A redirect response that sends the authenticated user to the home page.
    """
    code = request.GET.get("code")
    try:
        auth_response = workos.user_management.authenticate_with_code(
            code=code,  # type: ignore
            session={"seal_session": True, "cookie_password": cookie_password},  # type: ignore
        )
        response = redirect("home")
        response.set_cookie(
            "wos_session",
            auth_response.sealed_session,
            secure=True,
            httponly=True,
            samesite="Lax",
        )
        user = authenticate(request, sealed_session=auth_response.sealed_session)
        if user is not None:
            login(request, user)
    except Exception:
        logger.exception("Error authenticating with code")  # noqa
        message = (
            "Oops, an error occurred while trying to log you in."
            " Please try again later."
        )
        messages.error(request, message)
        return redirect("home")
    else:
        return response


def logout_(request: HttpRequest) -> HttpResponseRedirect:
    """Returns the user to the home page after deleting their cookie."""
    response = redirect("home")
    response.delete_cookie("wos_session")
    logout(request)
    return response


def profile(request: HttpRequest) -> HttpResponse:
    """Returns the view profile page for the user."""
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        context = {"user_profile": profile}
        return render(request, "auth_/profile.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")


def phi(request: HttpRequest) -> HttpResponse:
    """Returns form for PHI agreement."""
    if request.method == "POST":
        form = PHIForm(request.POST)
        if form.is_valid() and form.agree:
            p = UserProfile.objects.get(user=request.user)
            p.has_signed_phi_agreement = True
            p.save()
            messages.success(request, "PHI agreement signed.")
            return redirect("profile")
    else:
        form = PHIForm()
    return render(request, "auth_/phi.html", {"form": form})
