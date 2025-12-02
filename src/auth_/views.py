"""Provides views for the auth_ app."""

import os

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from workos import WorkOSClient

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
)


def login(request: HttpRequest) -> HttpResponseRedirect:
    """Logs the user in.

    Returns:
        A redirect response that sends the user to WorkOS's hosted login page.
    """
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
            code=code  # type: ignore
        )
        print(auth_response)  # noqa
        return redirect("home")

    except Exception as e:
        print("Error authenticating with code", e)  # noqa
        return redirect("woslogin")
