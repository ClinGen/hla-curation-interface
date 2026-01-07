"""Provides a custom WorkOS authentication backend."""

import logging
import os
from typing import Any

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpRequest
from workos import WorkOSClient

from core.models import UserProfile

logger = logging.getLogger(__name__)

workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
)

cookie_password = os.getenv("WORKOS_COOKIE_PASSWORD")


class WorkOSBackend(BaseBackend):
    """Enables authentication via WorkOS."""

    def authenticate(
        self,
        request: HttpRequest | None,
        **kwargs: Any,  # noqa: ANN401 (This matches the signature of the base class.)
    ) -> User | None:
        """Authenticates the user based on the WorkOS sealed session.

        Args:
             request: The HttpRequest object.
             kwargs: Keyword arguments (may include sealed_session for initial login).

        Returns:
             The User object for the authenticated user or None if we were unable to
             authenticate the user.
        """
        # Check if sealed_session was passed directly, e.g., during the initial login.
        sealed_session = kwargs.get("sealed_session") or request.COOKIES.get(
            "wos_session"
        )
        if not sealed_session:
            logger.warning("Unable to find sealed session")
            return None
        try:
            logger.warning("Attempting to load session")
            session = workos.user_management.load_sealed_session(
                sealed_session=sealed_session,
                cookie_password=cookie_password,
            )
            auth_response = session.authenticate()
            if not auth_response.authenticated:
                try:
                    logger.info("Attempting to refresh session")
                    refresh_result = session.refresh()
                    if not refresh_result.authenticated:
                        return None
                    auth_response = refresh_result
                except Exception:  # noqa (Normally I don't like doing this, but this is how WorkOS does it.)
                    logger.exception("Error refreshing session")
                    return None
            user_info = auth_response.user
            user, created_user = User.objects.get_or_create(
                username=user_info.email,
                defaults={
                    "email": user_info.email,
                    "first_name": user_info.first_name or "",
                    "last_name": user_info.last_name or "",
                },
            )
            profile, created_profile = UserProfile.objects.get_or_create(user=user)
            if created_user:
                logger.info(f"Created new user: {user}")
            if created_profile:
                logger.info(f"Created new profile: {profile}")
        except Exception:  # noqa (Normally I don't like doing this, but this is how WorkOS does it.)
            logger.exception("Error authenticating")
            return None
        else:
            return user

    def get_user(self, user_id: int) -> User | None:
        """Returns a user based on the provided user_id."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"User with user ID {user_id} does not exist")
            return None
