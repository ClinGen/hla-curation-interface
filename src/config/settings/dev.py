"""Provide development settings."""

from django.contrib import messages

from .base import *  # noqa: F403 (We want to import everything.)

DEBUG = True

ALLOWED_HOSTS: list[str] = []

MESSAGE_LEVEL = messages.DEBUG

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
