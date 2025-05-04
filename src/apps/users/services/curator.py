"""Provide create, update, and delete logic for `Curator` objects."""

from django.contrib.auth.models import User

from apps.users.models import Curator


def new_curator(user: User) -> Curator:
    """Return a newly created `Curator` object based on the given `user`."""
    return Curator.objects.create(user=user)
