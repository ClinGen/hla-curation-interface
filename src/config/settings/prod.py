"""Provides production settings."""

import os

from django.contrib import messages

from .base import *  # ruff: ignore[undefined-local-with-import-star] (We want to import everything.)
from .base import SUBDOMAIN

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

# Send email through Amazon SES. See How to Configure Email in docs/how-to.md.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": "email-smtp.us-west-2.amazonaws.com",
            "port": 587,
            "use_tls": True,
            "username": os.getenv("EMAIL_HOST_USER", ""),
            "password": os.getenv("EMAIL_HOST_PASSWORD", ""),
            # Keep a stuck SMTP connection from hanging a request or the backup.
            "timeout": 10,
        },
    },
}

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", f"noreply@{SUBDOMAIN}.clinicalgenome.org"
)

SERVER_EMAIL = DEFAULT_FROM_EMAIL
