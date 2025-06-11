"""Provides authentication backends for the firebase app."""

import logging
from typing import Any

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpRequest

from core.crud import create_user_profile, update_user_profile
from firebase.clients import get_token_info
from firebase.crud import create_firebase_user, read_firebase_user, update_firebase_user

logger = logging.getLogger(__name__)


class FirebaseBackend(BaseBackend):
    """Enables authentication via Google's Firebase authentication service."""

    def authenticate(
        self,
        request: HttpRequest | None,  # noqa: ARG002 (The request parameter is required here.)
        **kwargs: Any,  # noqa: ANN401 (This matches the signature of the base class.)
    ) -> User | None:
        """Authenticates the user based on the provided ID token.

        Args:
             request: The HttpRequest object.
             kwargs: Keyword arguments containing id_token, the JSON Web Token that
                     needs to be verified using the Firebase Admin SDK.

        Returns:
             The User object for the authenticated user or None if we were unable to
             authenticate the user.
        """
        id_token = kwargs.get("id_token")
        if id_token is None:
            return None
        info: Any = get_token_info(id_token)
        if info is None:
            return None
        user = read_firebase_user(info.get("username"))
        if user is None:
            user = create_firebase_user(info.get("username"), info.get("email"))
            create_user_profile(
                username=info.get("username"),
                email_verified=info.get("email_verified"),
                photo_url=info.get("photo_url"),
                display_name=info.get("display_name"),
            )
        else:
            user = update_firebase_user(info.get("username"), info.get("email"))
            update_user_profile(
                username=info.get("username"),
                email_verified=info.get("email_verified"),
                photo_url=info.get("photo_url"),
                display_name=info.get("display_name"),
            )
        return user

    def get_user(self, user_id: str) -> User | None:
        """Returns a user based on the provided user_id."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
