# `config`

## Directory Overview

`config` is the Django project configuration package. It contains the split settings
hierarchy (`base`, `dev`, `prod`), the root URL dispatcher that wires together all app
URL modules, and the WSGI entry point used by the production server. Nothing
application-specific lives here; all domain logic belongs in the individual Django apps.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `settings/__init__.py`

Empty file; marks this directory as a Python package.

### `settings/base.py`

Defines settings shared across all environments: installed apps, middleware (including
WhiteNoise for static files and `simple_history` for model history tracking), template
configuration, the SQLite database, the WorkOS authentication backend alongside Django's
default `ModelBackend`, and Sentry error monitoring and tracing initialization. Also
sets `django-tables2` and `LOGIN_URL`.

### `settings/dev.py`

Extends `base.py` for local development: enables `DEBUG`, sets `ALLOWED_HOSTS` to an
empty list, sets the message level to `DEBUG`, disables timezone support
(`USE_TZ = False`), and configures a console logging handler that emits all log levels
down to `DEBUG`.

### `settings/prod.py`

Extends `base.py` for production deployments on `hci.clinicalgenome.org` and
`hci-test.clinicalgenome.org`: disables `DEBUG`, restricts `ALLOWED_HOSTS`, sets the
message level to `INFO`, enables timezone support (`USE_TZ = True`), and configures both
a console handler and a rotating file handler (5 MB max, 5 backups) that writes verbose
logs to `../logs/hci.log`.

### `urls.py`

Root URL configuration; mounts the Django admin at `admin/` and delegates URL routing
for each Django app (`core`, `allele`, `auth_`, `curation`, `disease`, `haplotype`,
`publication`, `repo`) to their respective `urls.py` modules. `core` is mounted at the
root path (`""`).

### `wsgi.py`

WSGI application entry point; loads environment variables from `.env` via
`python-dotenv`, then exposes the Django WSGI application object for use by a WSGI
server such as Gunicorn.
