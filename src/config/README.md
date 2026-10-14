# `config`

This directory is the Django configuration package for the HLA Curation Interface. It contains the root URL routing, WSGI entry point, and a layered settings system that separates concerns across base, development, production, and test environments.

### `__init__.py`

Empty file that marks `config` as a Python package.

### `settings/__init__.py`

Empty file that marks `settings` as a Python package.

### `settings/base.py`

Defines settings shared across all environments, including installed apps, middleware, database (SQLite), static file handling via WhiteNoise, Clerk authentication keys and backends, Sentry initialization, the custom `django-tables2` template, database backups with `django-dbbackup`, the `SUBDOMAIN` setting, and `ALERT_EMAILS`, the comma-separated addresses that alerts go to. It doesn't set `ADMINS`, because that makes Django email every server error, which Sentry already reports. Backups go to the S3 bucket named by `DBBACKUP_BUCKET_NAME` when it's set, using the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables, and to a `backups/` directory next to `src/` otherwise. Backups that `django-dbbackup` names itself go under `daily/` and include `SUBDOMAIN` (`hci`, `hci-test`, or `dev` by default). Environment-specific settings files import from this module.

### `settings/dev.py`

Extends `base.py` with development-specific overrides: `DEBUG = True`, no `ALLOWED_HOSTS` restriction, `MESSAGE_LEVEL` set to `DEBUG`, console email through `MAILERS`, and a console logging configuration that suppresses noisy `httpcore` and `urllib3` debug output. Timezone support (`USE_TZ`) is disabled.

### `settings/prod.py`

Extends `base.py` with production-specific overrides: `DEBUG = False`, `ALLOWED_HOSTS` restricted to the ClinGen production and test hostnames, `MESSAGE_LEVEL` set to `INFO`, and logging to stderr only, with the level, logger name, and message. Gunicorn runs under systemd, so journald collects stderr and adds the timestamp. Email goes through Amazon SES over SMTP, configured in `MAILERS` from the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables, from `DEFAULT_FROM_EMAIL` (`noreply@<SUBDOMAIN>.clinicalgenome.org` by default). Timezone support (`USE_TZ`) is enabled.

### `settings/test.py`

Extends `dev.py` for use during test runs. Keeps email in memory with the locmem backend, disables Sentry to prevent background HTTP flushes from polluting test output, and replaces the console log handler with a null handler so logs are suppressed by default and only surfaced by pytest for failing tests.

### `tests.py`

Houses `ProdLoggingTest`, which imports the production settings with Sentry patched out and checks that they log only to the console, with the logger name, and define no log file; `AlertEmailsSettingTest`, which checks how `ALERT_EMAILS` is parsed; and `EmptyEnvironmentVariableTest`, which checks that an empty `SUBDOMAIN` or `DEFAULT_FROM_EMAIL` falls back to its default.

### `urls.py`

Defines the project-level URL configuration. It routes `admin/backup/` to the admin's Back up now view, and routes requests to the `core`, `admin`, `allele`, `auth_`, `curation`, `disease`, `haplotype`, `publication`, and `repo` apps.

### `wsgi.py`

Configures the WSGI application entry point. Loads environment variables from the `.env` file via `python-dotenv` before initializing the Django application.
