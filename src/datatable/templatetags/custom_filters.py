"""Provides custom template filters."""

from typing import Any

from django.db.models import Model
from django.http import HttpRequest
from django.template.defaulttags import register


@register.filter
def get_val(model: Model, field_name: str) -> Any | str:  # noqa: ANN401 (We don't know the type of the value.)
    """Returns the value of a model instance's field given the field name."""
    if hasattr(model, field_name):
        return getattr(model, field_name)
    return None


@register.filter
def get_item(dictionary: dict, key: str) -> Any | str:  # noqa: ANN401 (We don't know the type of the value.)
    """Returns the value to a key in a dictionary."""
    return dictionary.get(key)


@register.filter
def in_get(value: str, request: HttpRequest) -> bool:
    """Returns whether the value is present in request.GET."""
    return value in request.GET
