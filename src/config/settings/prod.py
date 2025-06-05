"""Provide production settings."""

from .base import *  # noqa: F403 (We want to import everything.)

DEBUG = False

ALLOWED_HOSTS = [
    "hci-test.clinicalgenome.org",
    "hci.clinicalgenome.org",
]
