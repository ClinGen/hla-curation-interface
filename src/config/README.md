# `config`

This directory is the Django configuration package for the HLA Curation Interface. It contains the root URL routing, WSGI entry point, and a layered settings system that separates concerns across base, development, production, and test environments.

### `__init__.py`

Empty file that marks `config` as a Python package.

### `settings/__init__.py`

Empty file that marks `settings` as a Python package.

### `settings/base.py`

Defines settings shared across all environments, including installed apps, middleware, database (SQLite), static file handling via WhiteNoise, Clerk authentication keys and backends, Sentry initialization, the custom `django-tables2` template, and database backups with `django-dbbackup`. Backups go to the S3 bucket named by `DBBACKUP_BUCKET_NAME` when it's set, using the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables, and to a `backups/` directory next to `src/` otherwise. Backups that `django-dbbackup` names itself go under `daily/` and include the `SUBDOMAIN` environment variable (`hci`, `hci-test`, or `dev` by default). Environment-specific settings files import from this module.

### `settings/dev.py`

Extends `base.py` with development-specific overrides: `DEBUG = True`, no `ALLOWED_HOSTS` restriction, `MESSAGE_LEVEL` set to `DEBUG`, and a console logging configuration that suppresses noisy `httpcore` and `urllib3` debug output. Timezone support (`USE_TZ`) is disabled.

### `settings/prod.py`

Extends `base.py` with production-specific overrides: `DEBUG = False`, `ALLOWED_HOSTS` restricted to the ClinGen production and test hostnames, `MESSAGE_LEVEL` set to `INFO`, and logging to stderr only, with the level, logger name, and message. Gunicorn runs under systemd, so journald collects stderr and adds the timestamp. Timezone support (`USE_TZ`) is enabled.

### `settings/test.py`

Extends `dev.py` for use during test runs. Disables Sentry to prevent background HTTP flushes from polluting test output, and replaces the console log handler with a null handler so logs are suppressed by default and only surfaced by pytest for failing tests.

### `tests.py`

Houses `ProdLoggingTest`, which imports the production settings with Sentry patched out and checks that they log only to the console, with the logger name, and define no log file.

### `urls.py`

Defines the project-level URL configuration. It routes `admin/backup/` to the admin's Back up now view, and routes requests to the `core`, `admin`, `allele`, `auth_`, `curation`, `disease`, `haplotype`, `publication`, and `repo` apps.

### `wsgi.py`

Configures the WSGI application entry point. Loads environment variables from the `.env` file via `python-dotenv` before initializing the Django application.
