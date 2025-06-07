"""Provide development settings."""

from django.contrib import messages

from .base import *  # noqa: F403 (We want to import everything.)

DEBUG = True

ALLOWED_HOSTS: list[str] = []

MESSAGE_LEVEL = messages.DEBUG
