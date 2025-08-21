"""Centralizes create, read, update, and delete logic for the firebase app."""

import logging

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


def create_firebase_user(uid: str, email: str) -> User:
    """Creates a Firebase User object in the database.

    Args:
         uid: The user ID from Firebase.
         email: An email string, e.g., foo@bar.org.

    Returns:
        The User object in the database with the given uid. If the User object already
        exists in the database, that User object is returned.
    """
    logger.info(f"Got request to create new Firebase user with uid {uid}")
    user = read_firebase_user(uid)
    if user is None:
        logger.info("Creating new user")
        user = User.objects.create(username=uid, email=email, is_active=False)
    return user


def read_firebase_user(uid: str) -> User | None:
    """Reads a Firebase User object from the database.

    Args:
         uid: The user ID from Firebase.

    Returns:
        The User object in the database with the given uid. If the User object doesn't
        exist in the database, None is returned.
    """
    try:
        user = User.objects.get(username=uid)
    except User.DoesNotExist:
        logger.info(f"User with uid {uid} does not exist")
        user = None
    return user


def update_firebase_user(uid: str, email: str) -> User | None:
    """Updates a User object with information from Firebase.

    Args:
         uid: The user ID from Firebase.
         email: An email string, e.g., foo@bar.org.

    Returns:
        The User object with updated information passed to the function. If the User
        object doesn't exist in the database, None is returned.
    """
    logger.info(f"Got request to update Firebase user with uid {uid}")
    user = read_firebase_user(uid)
    if user is None:
        logger.warning(f"Unable to find user with uid {uid}")
        return None
    if email != user.email:
        logger.warning(f"Updating user's email from {user.email} to {email}")
        user.email = email
        user.save()
    return user
