# `config`

This directory contains the Django project configuration for the HLA Curation
Interface (HCI). It is the package that Django treats as the project root: it
defines the root URL configuration, the WSGI entry point used by production
servers, and the settings modules that wire up installed apps, middleware,
templates, the database, static files, authentication, and logging. Settings
are split into a `base` module shared by every environment and per-environment
modules (`dev` and `prod`) that override behavior such as `DEBUG`,
`ALLOWED_HOSTS`, message levels, time-zone handling, and logging handlers.

### `__init__.py`

Marks the directory as a Python package.

### `settings/__init__.py`

Marks the directory as a Python package.

### `settings/base.py`

Shared settings used by every environment. Initializes Sentry error monitoring,
reads the deployed Git SHA from `version.txt` (falling back to `"dev"`),
declares `INSTALLED_APPS` (Django contrib apps, WhiteNoise, and the HCI apps),
`MIDDLEWARE`, `TEMPLATES` (including the `common.context_processors.git_sha`
context processor), the SQLite `DATABASES` config, password validators, the
`WorkOSBackend` plus default `ModelBackend` authentication backends, static
files config (served via WhiteNoise's `CompressedManifestStaticFilesStorage`),
and `LOGIN_URL`. Also sets `SECURE_CROSS_ORIGIN_OPENER_POLICY` to
`"same-origin-allow-popups"` so Firebase-based Google and Microsoft login
popups work.

### `settings/dev.py`

Development overrides. Enables `DEBUG`, leaves `ALLOWED_HOSTS` empty, sets the
message level to `DEBUG`, configures a single console logging handler at
`DEBUG` level, and disables timezone-aware datetimes (`USE_TZ = False`).

### `settings/prod.py`

Production overrides. Disables `DEBUG`, restricts `ALLOWED_HOSTS` to
`hci-test.clinicalgenome.org` and `hci.clinicalgenome.org`, sets the message
level to `INFO`, configures both console and rotating-file logging (5 MB per
file, 5 backups, written to `../logs/hci.log` relative to `BASE_DIR`), and
enables timezone-aware datetimes (`USE_TZ = True`).

### `urls.py`

Root URL configuration. Mounts the Django admin at `admin/` and includes the
URL configurations for the `core`, `allele`, `auth_`, `curation`, `disease`,
`haplotype`, `publication`, and `repo` apps under their respective path
prefixes.

### `wsgi.py`

WSGI application entry point. Loads environment variables from the `.env` file
via `python-dotenv` before constructing the WSGI application so settings that
read from the environment see the expected values.
