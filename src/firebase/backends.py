"""Provides authentication backends for the firebase app."""

import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpRequest
from firebase_admin import auth
from firebase_admin.auth import (
    CertificateFetchError,
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
)

logger = logging.getLogger(__name__)


class FirebaseBackend(BaseBackend):
    """Enables authentication via Google's Firebase authentication service."""

    def authenticate(
        self,
        request: HttpRequest,  # noqa: ARG002 (The request parameter is required here.)
        id_token: str | None = None,
    ) -> User | None:
        """Authenticates the user based on the provided ID token.

        Args:
             request: The HttpRequest object.
             id_token: The JSON Web Token that needs to be verified using the Firebase
                       Admin SDK.

        Returns:
             The User object for the authenticated user or None if we were unable to
             authenticate the user.
        """
        user = None
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token.get("uid")
            email = decoded_token.get("email")
            user, _ = User.objects.get_or_create(
                username=uid, defaults={"email": email}
            )
        except ValueError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        except CertificateFetchError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        except ExpiredIdTokenError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        except RevokedIdTokenError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        except InvalidIdTokenError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        except UserDisabledError as exc:
            error_message = f"Unable to authenticate user: {exc}"
            logger.exception(error_message)
        return user

    def get_user(self, user_id: str) -> User | None:
        """Returns a user based on the provided user_id."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
