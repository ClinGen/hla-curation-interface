"""Provides configuration for the Jinja templating engine."""

from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse
from googleapiclient.http import HttpRequest
from jinja2 import Environment


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
