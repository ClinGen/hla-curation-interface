# `config`

The `config` directory is the Django project configuration package. It holds the split
settings hierarchy (base, dev, prod), the root URL dispatcher that wires together all
app URL modules, and the WSGI entry point used by the production server.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `settings/__init__.py`

Empty file; marks this directory as a Python package.

### `settings/base.py`

Defines settings shared across all environments, including installed apps, middleware,
template configuration, the SQLite database, static file storage via WhiteNoise, the
WorkOS authentication backend, and Sentry error monitoring initialization.

### `settings/dev.py`

Extends `base.py` for local development: enables `DEBUG`, allows all hosts, sets the
message level to `DEBUG`, and configures a console logging handler that emits all log
levels.

### `settings/prod.py`

Extends `base.py` for the production deployment on `hci.clinicalgenome.org`: disables
`DEBUG`, restricts `ALLOWED_HOSTS`, sets the message level to `INFO`, and configures
both a console handler and a rotating file handler that writes to `../logs/hci.log`.

### `urls.py`

Root URL configuration; mounts the Django admin at `admin/` and delegates URL routing
for each Django app (`core`, `allele`, `auth_`, `curation`, `disease`, `haplotype`,
`publication`, `repo`) to their respective `urls.py` modules.

### `wsgi.py`

WSGI application entry point; loads environment variables from `.env` via
`python-dotenv` and exposes the Django WSGI application object for use by a WSGI server
such as Gunicorn.
