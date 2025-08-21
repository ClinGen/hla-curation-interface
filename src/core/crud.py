"""Centralizes create, read, update, and delete logic for the core app."""

import logging

from django.contrib.auth.models import User

from core.models import UserProfile
from firebase.crud import read_firebase_user

logger = logging.getLogger(__name__)


def create_user_profile(
    *,
    username: str,
    email_verified: bool,
    photo_url: str,
    display_name: str,
    provider: str,
) -> tuple[UserProfile, User] | None:
    """Creates a UserProfile object in the database.

    Args:
         username: The User object's username.
         email_verified: Whether the user's email has been verified.
         photo_url: A URL for the user's profile picture.
         display_name: The user's display name.
         provider: The method used to log the user in, e.g., Google.

    Returns:
        A tuple containing the UserProfile object and the User object in the database
        with the given username. If the User object doesn't exist yet, we return None.
    """
    logger.info(f"Got request to create user profile for {username}")
    user = read_firebase_user(username)
    if user is None:
        logger.warning(f"Unable to find user with username {username}")
        return None
    logger.info("Creating user profile")
    user_profile = UserProfile.objects.create(
        user=user,
        firebase_uid=username,
        firebase_email_verified=email_verified,
        firebase_photo_url=photo_url,
        firebase_display_name=display_name,
        firebase_sign_in_provider=provider,
    )
    return user_profile, user


def read_user_profile(username: str) -> tuple[UserProfile, User] | None:
    """Reads a UserProfile object from the database.

    Args:
        username: The User object's username.

    Returns:
        A tuple containing the UserProfile object and the User object in the database
        with the given username. If either the UserProfile object or the User object
        can't be found, we return None.
    """
    user = read_firebase_user(username)
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        logger.warning(f"User profile does not exist for user with username {username}")
        user_profile = None
    if user is None or user_profile is None:
        logger.warning("Unable to find user and/or user profile")
        return None
    return user_profile, user


def update_user_profile(
    *,
    username: str,
    email_verified: bool,
    photo_url: str,
    display_name: str,
    provider: str,
) -> tuple[UserProfile, User] | None:
    """Updates a UserProfile object in the database.

    Args:
         username: The User object's username.
         email_verified: Whether the user's email has been verified.
         photo_url: A URL for the user's profile picture.
         display_name: The user's display name.
         provider: The method used to log the user in, e.g., Google.

    Returns:
        A tuple containing the newly updated UserProfile object and the User object in
        the database with the given username. If the UserProfile object or the User
        object doesn't exist, we return None.
    """
    logger.info(f"Got request to update user profile for user with username {username}")
    read = read_user_profile(username)
    if read is None:
        logger.warning(f"Unable to find user profile with username {username}")
        return None
    user_profile, user = read
    changed = False
    if user_profile.firebase_email_verified != email_verified:
        logger.info("Email verified")
        user_profile.firebase_email_verified = email_verified
        changed = True
    if user_profile.firebase_photo_url != photo_url:
        logger.info("Changing photo URL")
        user_profile.firebase_photo_url = photo_url
        changed = True
    if user_profile.firebase_display_name != display_name:
        logger.info("Changing display name")
        user_profile.firebase_display_name = display_name
        changed = True
    if user_profile.firebase_sign_in_provider != provider:
        logger.info("Changing sign in provider")
        user_profile.firebase_sign_in_provider = provider
        changed = True
    if changed:
        logger.info("Saving changes")
        user_profile.save()
    return user_profile, user
