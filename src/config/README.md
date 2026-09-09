# `config`

This directory is the Django configuration package for the HLA Curation Interface. It contains the root URL routing, WSGI entry point, and a layered settings system that separates concerns across base, development, production, and test environments.

### `__init__.py`

Empty file that marks `config` as a Python package.

### `settings/__init__.py`

Empty file that marks `settings` as a Python package.

### `settings/base.py`

Defines settings shared across all environments, including installed apps, middleware, database (SQLite), static file handling via WhiteNoise, Clerk authentication keys and backends, Sentry initialization, and the custom `django-tables2` template. Environment-specific settings files import from this module.

### `settings/dev.py`

Extends `base.py` with development-specific overrides: `DEBUG = True`, no `ALLOWED_HOSTS` restriction, `MESSAGE_LEVEL` set to `DEBUG`, and a console logging configuration that suppresses noisy `httpcore` and `urllib3` debug output. Timezone support (`USE_TZ`) is disabled.

### `settings/prod.py`

Extends `base.py` with production-specific overrides: `DEBUG = False`, `ALLOWED_HOSTS` restricted to the ClinGen production and test hostnames, `MESSAGE_LEVEL` set to `INFO`, and a rotating file logger (5 MB, 5 backups) alongside a console handler. Timezone support (`USE_TZ`) is enabled.

### `settings/test.py`

Extends `dev.py` for use during test runs. Disables Sentry to prevent background HTTP flushes from polluting test output, and replaces the console log handler with a null handler so logs are suppressed by default and only surfaced by pytest for failing tests.

### `urls.py`

Defines the project-level URL configuration, routing requests to the `core`, `admin`, `allele`, `auth_`, `curation`, `disease`, `haplotype`, `publication`, and `repo` apps.

### `wsgi.py`

Configures the WSGI application entry point. Loads environment variables from the `.env` file via `python-dotenv` before initializing the Django application.
