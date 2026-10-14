"""Provides production settings."""

from django.contrib import messages

from .base import *  # ruff: ignore[undefined-local-with-import-star] (We want to import everything.)

DEBUG = False

ALLOWED_HOSTS = [
    "hci-test.clinicalgenome.org",
    "hci.clinicalgenome.org",
]

MESSAGE_LEVEL = messages.INFO

# Log only to stderr. Gunicorn runs under systemd, so stderr goes to journald, which
# adds the timestamp, host, unit, and process ID, and handles rotation and retention.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

USE_TZ = True
