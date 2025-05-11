"""Defines permissions for CRUD (create, read, update, and delete) operations."""

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser, User

from apps.users.selectors.curator import get_curator


def can_delete(user: User | AbstractBaseUser | AnonymousUser) -> bool:
    """Returns whether a user can delete something in the HCI."""
    if user.is_authenticated:
        curator = get_curator(user.username)
        if curator:
            return curator.active_affiliation is not None
    return False
