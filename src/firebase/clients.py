"""Centralizes interactions with external data providers for the firebase app."""

import logging

from firebase_admin import auth
from firebase_admin.auth import UserNotFoundError
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)


def get_user_info(uid: str) -> dict | None:
    """Returns the Firebase user info given a Firebase uid."""
    info = None
    try:
        info = auth.get_user(uid)
    except ValueError as exc:
        error_message = f"Unable to get user info: {exc}"
        logger.exception(error_message)
    except UserNotFoundError as exc:
        error_message = f"Unable to get user info: {exc}"
        logger.exception(error_message)
    except FirebaseError as exc:
        error_message = f"Unable to get user info: {exc}"
        logger.exception(error_message)
    return info
