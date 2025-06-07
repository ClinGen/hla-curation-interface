"""Provide production settings."""

from django.contrib import messages

from .base import *  # noqa: F403 (We want to import everything.)

DEBUG = False

ALLOWED_HOSTS = [
    "hci-test.clinicalgenome.org",
    "hci.clinicalgenome.org",
]

MESSAGE_LEVEL = messages.INFO
