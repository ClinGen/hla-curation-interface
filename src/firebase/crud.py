"""Centralizes create, read, update, and delete logic for the firebase app."""

from django.contrib.auth.models import User


def create_firebase_user(uid: str, email: str) -> User:
    """Creates a Firebase User object in the database.

    Args:
         uid: The user ID from Firebase.
         email: An email string, e.g., foo@bar.org.

    Returns:
        The User object in the database with the given uid. If the User object already
        exists in the database, that User object is returned.
    """
    user = read_firebase_user(uid)
    if user is None:
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
    user = read_firebase_user(uid)
    if user is None:
        return None
    if email != user.email:
        user.email = email
        user.save()
    return user
