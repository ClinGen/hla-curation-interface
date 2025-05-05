"""Provide the settings for the dev environment.

The dev environment should be used for local development and in continuous
integration. The only significant difference between the dev environment and
the prod environment is that the dev environment uses an SQLite database instead
of a Postgres database.
"""

from django.contrib import messages

from .base import (  # noqa: F401 (We don't care about unused imports in this context.)
    ASGI_APPLICATION,
    AUTH_PASSWORD_VALIDATORS,
    BASE_DIR,
    DATABASES,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    LOGIN_URL,
    MIDDLEWARE,
    ROOT_URLCONF,
    SECRET_KEY,
    STATIC_ROOT,
    STATIC_URL,
    STATICFILES_DIRS,
    STORAGES,
    TEMPLATES,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
)

DEBUG = True

ALLOWED_HOSTS: list[str] = []

MESSAGE_LEVEL = messages.DEBUG
