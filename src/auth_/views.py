# mypy: ignore-errors
import logging
import os

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from workos import WorkOSClient
from workos.session import seal_session_from_auth_response

from auth_.forms import PHIForm
from auth_.models import UserProfile
from common.history import resolve_changes

logger = logging.getLogger(__name__)

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
        )
        sealed_session = seal_session_from_auth_response(
            access_token=auth_response.access_token,
            refresh_token=auth_response.refresh_token,
            user=auth_response.user.to_dict(),
            cookie_password=cookie_password,  # type: ignore
        )
        response = redirect("home")
        response.set_cookie(
            "wos_session",
            sealed_session,
            secure=True,
            httponly=True,
            samesite="Lax",
        )
        user = authenticate(request, sealed_session=sealed_session)
        if user is not None:
            login(request, user)
    except Exception:  # noqa (Normally I don't like doing this, but this is how WorkOS does it.)
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
    """Returns the profile page for the user."""
    if request.user.is_authenticated:
        p, _ = UserProfile.objects.get_or_create(user=request.user)
        context = {"user_profile": p}
        return render(request, "auth_/profile.html", context)
    messages.info(request, "Not logged in.")
    return redirect("login")


def profile_history(request: HttpRequest) -> HttpResponse:
    """Returns the history page for the current user's profile."""
    if not request.user.is_authenticated:
        messages.info(request, "Not logged in.")
        return redirect("login")
    p = get_object_or_404(UserProfile, user=request.user)
    return render(
        request, "auth_/history.html", {"user_profile": p, "history": p.history.all()}
    )


def profile_change(request: HttpRequest, history_id: int) -> HttpResponse:
    """Returns the change detail page for a single history record."""
    if not request.user.is_authenticated:
        messages.info(request, "Not logged in.")
        return redirect("login")
    p = get_object_or_404(UserProfile, user=request.user)
    record = p.history.get(history_id=history_id)
    prev_record = record.prev_record
    changes = resolve_changes(UserProfile, record, prev_record)
    return render(
        request,
        "auth_/change.html",
        {"user_profile": p, "record": record, "changes": changes},
    )


def phi(request: HttpRequest) -> HttpResponse:
    """Returns form for PHI agreement."""
    if request.method == "POST":
        form = PHIForm(request.POST)
        if form.is_valid() and form.agree:
            p = UserProfile.objects.get(user=request.user)  # type: ignore
            p.has_signed_phi_agreement = True
            p.save()
            messages.success(request, "PHI agreement signed.")
            return redirect("profile")
    else:
        form = PHIForm()
    return render(request, "auth_/phi.html", {"form": form})
