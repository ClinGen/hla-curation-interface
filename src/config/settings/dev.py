"""Provide the settings for the dev environment.

The dev environment should be used for local development and in continuous
integration. The only significant difference between the dev environment and
the prod environment is that the dev environment uses an SQLite database instead
of a Postgres database.
"""

from .base import (  # noqa: F401 (We don't care about unused imports in this context.)
    ASGI_APPLICATION,
    AUTH_PASSWORD_VALIDATORS,
    BASE_DIR,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
    MIDDLEWARE,
    ROOT_URLCONF,
    SECRET_KEY,
    STATIC_ROOT,
    STATIC_URL,
    STATICFILES_DIRS,
    TEMPLATES,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
)

DEBUG = True

ALLOWED_HOSTS: list[str] = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
