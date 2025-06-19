"""Provide production settings."""

import os

from django.contrib import messages

from .base import *  # noqa: F403 (We want to import everything.)
from .base import BASE_DIR

DEBUG = False

ALLOWED_HOSTS = [
    "hci-test.clinicalgenome.org",
    "hci.clinicalgenome.org",
]

MESSAGE_LEVEL = messages.INFO

LOG_FILE_NAME = "hci.log"

LOG_DIR = BASE_DIR.parent / "logs"
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / LOG_FILE_NAME
if not LOG_FILE.exists():
    LOG_FILE.touch()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {name} {message}",  # noqa: E501
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 5,  # 1024 * 1024 * 5 = 5 MB.
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
}
