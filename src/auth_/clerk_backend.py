"""Provides a custom Clerk authentication backend."""

import logging
import os
from typing import Any

from clerk_backend_api import Clerk
from clerk_backend_api.security.authenticaterequest import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpRequest

from auth_.models import UserProfile

logger = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "__session"


def _primary_email(user: Any) -> str | None:  # noqa: ANN401 (Clerk SDK types.)
    """Returns the primary email address for a Clerk user, if available."""
    email_id = getattr(user, "primary_email_address_id", None)
    addresses = getattr(user, "email_addresses", None) or []
    for address in addresses:
        if getattr(address, "id", None) == email_id:
            return getattr(address, "email_address", None)
    if addresses:
        return getattr(addresses[0], "email_address", None)
    return None


def _authorized_parties() -> list[str] | None:
    """Returns the configured list of authorized origins, if any."""
    raw = os.getenv("CLERK_AUTHORIZED_PARTIES")
    if not raw:
        return None
    return [part.strip() for part in raw.split(",") if part.strip()]


def _resolve_session_token(
    request: HttpRequest | None,
    kwargs: dict[str, Any],
) -> str | None:
    """Returns the Clerk session token from kwargs or the request cookies."""
    session_token = kwargs.get("session_token")
    if not session_token and request is not None:
        session_token = request.COOKIES.get(SESSION_COOKIE_NAME)
    return session_token


class _SessionTokenRequest:
    """Adapts a raw session token to the Requestish protocol for Clerk."""

    def __init__(self, session_token: str) -> None:
        self.headers = {"Authorization": f"Bearer {session_token}"}


def _load_clerk_user_info(
    session_token: str,
    secret_key: str,
) -> tuple[str, str, str, str] | None:
    """Verifies a Clerk session and loads the associated user's profile details.

    Args:
        session_token: The Clerk session JWT.
        secret_key: The Clerk instance's secret key.

    Returns:
        A ``(clerk_id, email, first_name, last_name)`` tuple on success, or ``None``
        on any verification or lookup failure.
    """
    options = AuthenticateRequestOptions(
        secret_key=secret_key,
        authorized_parties=_authorized_parties(),
    )
    try:
        state = authenticate_request(_SessionTokenRequest(session_token), options)
    except Exception:
        logger.exception("Error verifying Clerk session")
        return None
    if not state.is_authenticated or state.payload is None:
        logger.warning("Clerk session is not authenticated: %s", state.message)
        return None
    clerk_user_id = state.payload.get("sub")
    if not clerk_user_id:
        logger.warning("Clerk session payload is missing the subject claim")
        return None
    try:
        with Clerk(bearer_auth=secret_key) as clerk:
            clerk_user = clerk.users.get(user_id=clerk_user_id)
    except Exception:
        logger.exception("Error loading Clerk user %s", clerk_user_id)
        return None
    if clerk_user is None:
        logger.warning("Clerk user %s not found", clerk_user_id)
        return None
    email = _primary_email(clerk_user)
    if not email:
        logger.warning("Clerk user %s has no email address", clerk_user_id)
        return None
    first_name = getattr(clerk_user, "first_name", None) or ""
    last_name = getattr(clerk_user, "last_name", None) or ""
    return clerk_user_id, email, first_name, last_name


class ClerkBackend(BaseBackend):
    """Enables authentication via Clerk."""

    def authenticate(
        self,
        request: HttpRequest | None,
        **kwargs: Any,  # noqa: ANN401 (This matches the signature of the base class.)
    ) -> User | None:
        """Authenticates the user based on a Clerk session JWT.

        Args:
            request: The HttpRequest object.
            kwargs: Keyword arguments. May include ``session_token`` for the initial
                login flow (e.g., from the callback view).

        Returns:
            The User object for the authenticated user or None if we were unable to
            authenticate the user.
        """
        secret_key = os.getenv("CLERK_SECRET_KEY")
        if not secret_key:
            logger.warning("CLERK_SECRET_KEY is not configured")
            return None
        session_token = _resolve_session_token(request, kwargs)
        if not session_token:
            logger.warning("Unable to find Clerk session token")
            return None
        info = _load_clerk_user_info(session_token, secret_key)
        if info is None:
            return None
        _clerk_id, email, first_name, last_name = info
        user, created_user = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        _, created_profile = UserProfile.objects.get_or_create(user=user)
        if created_user:
            logger.info("Created new user: %s", user)
        if created_profile:
            logger.info("Created new profile for %s", user)
        return user

    def get_user(self, user_id: int) -> User | None:
        """Returns a user based on the provided user_id."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning("User with user ID %s does not exist", user_id)
            return None
