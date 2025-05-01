"""Provide the settings common to both the dev and prod environments."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "apps.home.apps.HomeAppConfig",
    "apps.curations.apps.CurationsAppConfig",
    "apps.diseases.apps.DiseasesAppConfig",
    "apps.markers.apps.MarkersAppConfig",
    "apps.publications.apps.PublicationsAppConfig",
    "apps.users.apps.UsersAppConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "apps" / "home" / "templates",
            BASE_DIR / "apps" / "curations" / "templates",
            BASE_DIR / "apps" / "markers" / "templates",
            BASE_DIR / "apps" / "publications" / "templates",
            BASE_DIR / "apps" / "users" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501 (Having a long line here is fine.)
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# URL to use when referring to static files located in `STATIC_ROOT`.
STATIC_URL = "static/"

# Set where production static files are served from.
STATIC_ROOT = BASE_DIR / "public"

# Set where static files that aren't specific to an application are located.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Set the default primary key field type.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
