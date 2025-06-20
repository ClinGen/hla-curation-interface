"""Centralizes interactions with external data providers for the firebase app."""

import logging

from firebase_admin import auth
from firebase_admin.auth import (
    CertificateFetchError,
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
)

logger = logging.getLogger(__name__)


def get_token_info(id_token: str | None) -> dict | None:
    """Returns the info from the ID token obtained from the frontend."""
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
        info = None
    else:
        username = decoded_token.get("uid", None)
        email = decoded_token.get("email", None)
        if username is None or email is None:
            return None
        email_verified = decoded_token.get("email_verified", False)
        photo_url = decoded_token.get("picture", "")
        display_name = decoded_token.get("name", "")
        provider = decoded_token.get("firebase", {}).get("sign_in_provider", "")
        info = {
            "username": username,
            "email": email,
            "email_verified": email_verified,
            "photo_url": photo_url,
            "display_name": display_name,
            "provider": provider,
        }
    return info
