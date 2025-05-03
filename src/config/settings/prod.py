"""Provide the settings for the prod environment.

The prod environment should be used for both the test server and the production
server.
"""

from .base import (  # noqa: F401 (We don't care about unused imports in this context.)
    ASGI_APPLICATION,
    AUTH_PASSWORD_VALIDATORS,
    BASE_DIR,
    DATABASES,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    LANGUAGE_CODE,
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

DEBUG = False

ALLOWED_HOSTS = [
    "hci-test.clinicalgenome.org",
    "hci.clinicalgenome.org",
]
