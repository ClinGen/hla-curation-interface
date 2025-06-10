"""Centralizes interactions with external data providers for the firebase app."""

import logging

from firebase_admin import auth
from firebase_admin.auth import (
    CertificateFetchError,
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
    UserNotFoundError,
)
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


def get_user_info(uid: str) -> dict | None:
    """Returns the Firebase user info given a Firebase uid."""
    try:
        info = auth.get_user(uid)
    except (ValueError, UserNotFoundError, FirebaseError) as exc:
        error_message = f"Unable to get user info: {exc}"
        logger.exception(error_message)
        info = None
    return info


def decode_token(id_token: str | None) -> dict | None:
    """Returns the decoded id_token obtained from the frontend."""
    try:
        decoded_token = auth.verify_id_token(id_token)
    except (
        ValueError,
        CertificateFetchError,
        ExpiredIdTokenError,
        RevokedIdTokenError,
        InvalidIdTokenError,
        UserDisabledError,
    ) as exc:
        error_message = f"Unable to decode token: {exc}"
        logger.exception(error_message)
        decoded_token = None
    return decoded_token
