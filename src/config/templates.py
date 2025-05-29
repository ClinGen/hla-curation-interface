"""Provides configuration for the Jinja templating engine."""

from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def environment(**options: dict) -> Environment:
    """Returns an environment object with the functions we need in templates."""
    env = Environment(**options)  # noqa: S701 (Per the docs, Django adds autoescape=True.)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
        }
    )
    return env
