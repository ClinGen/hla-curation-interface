"""Provides custom template filters."""

from typing import Any

from django.db.models import Model
from django.http import HttpRequest
from django.template.defaulttags import register

from repo.constants import PUBLIC_CURATION_FIELDS, PUBLIC_EVIDENCE_FIELDS


@register.filter
def get_val(model: Model, field_name: str) -> Any | str:  # ruff: ignore[any-type] (We don't know the type of the value.)
    """Returns the value of a model instance's field given the field name."""
    if hasattr(model, field_name):
        return getattr(model, field_name)
    return None


@register.filter
def get_item(dictionary: dict, key: str) -> Any | str:  # ruff: ignore[any-type] (We don't know the type of the value.)
    """Returns the value to a key in a dictionary."""
    return dictionary.get(key)


@register.filter
def in_get(value: str, request: HttpRequest) -> bool:
    """Returns whether the value is present in request.GET."""
    return value in request.GET


@register.filter
def is_public(field_name: str, kind: str) -> bool:
    """Returns whether a curation or evidence field is public in HLArepo.

    Evidence forms edit some decimals as text fields named <field>_string, so the
    suffix is dropped before looking the field up.

    Args:
        field_name: The model or form field name.
        kind: Either "curation" or "evidence".
    """
    fields = PUBLIC_CURATION_FIELDS if kind == "curation" else PUBLIC_EVIDENCE_FIELDS
    return field_name.removesuffix("_string") in fields
