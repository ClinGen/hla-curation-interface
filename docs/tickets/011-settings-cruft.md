# Settings Cruft

## The Problem

The settings modules in `src/config/settings/` (`base.py`, `dev.py`, `prod.py`,
`test.py`) have accumulated through several auth providers (Firebase, then WorkOS,
then Clerk) and several tooling changes (mypy to ty). The note that prompted this
ticket gave `SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"` as an
example. That setting existed only for Firebase's Google and Microsoft popup login,
and it **has already been removed** in commit ce8ef5f ("Add Clerk"). The rest of the
audit is still worth doing: several settings duplicate Django's defaults, one
environment mismatch could hide bugs, and a few leftovers outside `settings/` refer to
tools we no longer use.

The goal is to remove what is clearly dead, and to get a decision on what only looks
dead.

## The Technical Plan

Make one small cleanup commit for the "safe to remove" items. Collect the "needs
checking" items as Open Questions, and handle each one after the user answers. Leave
`LOGGING` and the log-file setup in `prod.py` alone, because
`docs/plans/006-logging.md` already covers them.

### Safe to remove

1. **`MESSAGE_LEVEL = messages.INFO` in `prod.py`,** and the
   `from django.contrib import messages` import that only it uses. `INFO` is Django's
   default `MESSAGE_LEVEL`.
2. **`ALLOWED_HOSTS: list[str] = []` in `dev.py`.** This is Django's default. With
   `DEBUG = True`, Django already allows `localhost`, `127.0.0.1`, and `[::1]`.
3. **The `firebase-account-key*` entry in `.gitignore`.** Firebase auth is gone, and
   nothing in the repo references Firebase outside old plans.
4. **`CLERK_SIGN_IN_URL: "dummy"` in `.github/workflows/ci.yml` (two jobs) and
   `.github/workflows/codecov.yml`.** No settings module reads it, and
   `docs/plans/005-clerk-auth.md` says it isn't needed.

### Keep (they look redundant, but they aren't)

- `from .base import BASE_DIR` in `prod.py`: this duplicates the star import, but it
  keeps ruff from flagging `BASE_DIR` as possibly undefined when used after a star
  import.
- `LANGUAGE_CODE = "en-us"` and `TIME_ZONE = "UTC"`: these are Django's defaults, but
  stating them explicitly is useful documentation for an app that stores timestamps.
- `"whitenoise.runserver_nostatic"`, `DJANGO_TABLES2_TEMPLATE`, `LOGIN_URL` (imported
  by `src/auth_/permissions.py`), `GIT_SHA`, and `ENV` (used by
  `src/common/context_processors.py`) are all in use.

### Needs checking

These are listed in Open Questions:

- `USE_TZ` differs between environments. `dev.py` sets it to `False` and `prod.py`
  sets it to `True`. `test.py` inherits from `dev.py`, and pytest always uses
  `--ds=config.settings.test` (see `pyproject.toml`), so **tests run with naive
  datetimes while production uses aware ones**. The CI's
  `DJANGO_SETTINGS_MODULE: "config.settings.prod"` doesn't change this, because
  `--ds` takes precedence. This isn't cruft, but it's the most important finding:
  timezone bugs can pass the test suite. The likely fix is `USE_TZ = True` in
  `base.py`, removed from `dev.py` and `prod.py`.
- `AUTH_PASSWORD_VALIDATORS` and `django.contrib.auth.backends.ModelBackend` in
  `AUTHENTICATION_BACKENDS` only matter for password logins. Curators log in through
  Clerk (`auth_.backends.ClerkBackend`, which already subclasses `ModelBackend` for
  permission checks). They are still needed if anyone logs in to `/admin/` with a
  Django password (e.g., a superuser made with `createsuperuser`).
- `sentry_sdk.init(send_default_pii=True, traces_sample_rate=1.0)` in `base.py`: this
  isn't cruft, but it's worth a deliberate decision for an app whose users sign a PHI
  agreement. `send_default_pii=True` sends user IDs, emails, IP addresses, and request
  data to Sentry. A 100% trace sample rate is fine at our traffic but is usually
  lowered.
- `USE_I18N = True`: the app has no translations. Setting it to `False` is harmless,
  but it also changes nothing visible. Low value.
- `MESSAGE_LEVEL = messages.DEBUG` in `dev.py`: no code calls `messages.debug`, so
  this has no effect. It's harmless to keep if the user wants debug messages to
  remain available.
- `[tool.django-stubs]` in `pyproject.toml` configures the mypy django-stubs plugin,
  but the project moved from mypy to ty (commit 2a89a65). The `django-stubs` package
  may still help ty, but the config table is probably unused. (This is outside
  `settings/`, but it's the same kind of cruft.)

Also related, but out of scope: `pyproject.toml` has `readme = "README.rst"`, but the
file is `README.md`. `ClerkBackend.authenticate` stage 2 (the WorkOS email migration
path in `src/auth_/backends.py`) can be removed once every user has a `clerk_user_id`.
`docs/design.md` and `src/README.md` still describe WorkOS as the auth provider.

## Open Questions

1. **May we set `USE_TZ = True` everywhere?** This blocks the `USE_TZ` step. Check the
   dev database and any code that builds naive datetimes (`datetime.now()` without a
   timezone) first. Run the tests with the change to see what breaks.
2. **Does anyone log in to `/admin/` with a Django password?** If not,
   `ModelBackend` and `AUTH_PASSWORD_VALIDATORS` can go. If so, keep both. This blocks
   the auth-settings step.
3. **Are `send_default_pii=True` and `traces_sample_rate=1.0` intended?** This blocks
   only the Sentry step.
4. **Should the minor items (`USE_I18N`, dev `MESSAGE_LEVEL`, `[tool.django-stubs]`)
   be removed?** This doesn't block the main cleanup.

## Detailed Implementation

### Step 1 — Remove the safe items

#### `src/config/settings/prod.py` — modify

Delete `MESSAGE_LEVEL = messages.INFO` and the `messages` import.

#### `src/config/settings/dev.py` — modify

Delete `ALLOWED_HOSTS: list[str] = []`.

#### `.gitignore` and the `.github/workflows` files — modify

Delete the `firebase-account-key*` line from `.gitignore`, and delete the
`CLERK_SIGN_IN_URL` env entries from `.github/workflows/ci.yml` and
`.github/workflows/codecov.yml`.

#### `src/config/README.md` — modify

Update the `settings/dev.py` and `settings/prod.py` entries (remove the mentions of
`MESSAGE_LEVEL` set to `INFO` and of no `ALLOWED_HOSTS` restriction).

Verification: `just ci` passes, and `uv run python src/manage.py check --deploy
--settings=config.settings.prod` reports no new warnings. It already reports
security.W004 (HSTS), W008 (`SECURE_SSL_REDIRECT`), W012 (`SESSION_COOKIE_SECURE`),
and W016 (`CSRF_COOKIE_SECURE`), plus W009 with a local dev secret key. Caddy
terminates TLS (and by default redirects HTTP to HTTPS), so W004 and W008 may be
intentional. Setting
the two secure-cookie flags in `prod.py` is a reasonable follow-up, but it isn't cruft
removal, so it isn't part of this ticket.

### Step 2 — Make `USE_TZ` consistent (blocked on Open Question 1)

#### `src/config/settings/base.py`, `dev.py`, `prod.py` — modify

Set `USE_TZ = True` in `base.py`, and delete it from `dev.py` and `prod.py`.

#### Tests

Run the full suite. Fix any `RuntimeWarning: DateTimeField ... received a naive
datetime` by using `django.utils.timezone.now()`. Add a test in `src/core/tests.py`
(or a new settings test) that asserts `settings.USE_TZ` is `True`, so the environments
can't drift apart again. Update `src/config/README.md`.

### Step 3 — Password-auth settings (blocked on Open Question 2)

If no one uses password logins, remove `ModelBackend` from `AUTHENTICATION_BACKENDS`
and delete `AUTH_PASSWORD_VALIDATORS` from `base.py`. Confirm that the tests in
`src/auth_/tests.py` still pass (`ClerkBackend` inherits the permission methods).
Update `src/config/README.md`.

### Step 4 — Sentry options (blocked on Open Question 3)

Apply the user's choice to the `sentry_sdk.init` call in `base.py`, and update
`src/config/README.md`.

## Sources

- Notes: "HCI: Check `base.py` for cruft", e.g.,
  `SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"`
