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
