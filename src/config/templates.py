"""Provides configuration for the Jinja templating engine."""

import typing

from django.contrib import messages
from django.http import HttpRequest
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


# We don't type check this function because mypy doesn't understand why we're passing
# the unpacked options dictionary to Jinja2's Environment class. I would prefer to
# ignore the offending line, but there's already a comment that ignores a lint rule for
# that line.
@typing.no_type_check
def environment(**options: dict) -> Environment:
    """Returns an environment object with the functions we need in templates."""
    env = Environment(**options)  # noqa: S701 (Per the docs, Django adds autoescape=True.)

    def get_messages(request: HttpRequest) -> list:
        """Returns messages for the current request."""
        return messages.get_messages(request)

    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "get_messages": get_messages,
        }
    )
    return env
