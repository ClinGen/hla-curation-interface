# Auth

This directory contains the `auth_` Django app for the HLA Curation Interface
(HCI). The app handles user authentication and authorization, integrating with
WorkOS for hosted login, extending Django's built-in `User` model with an
HCI-specific `UserProfile`, and exposing the permission primitives used by
other apps to gate curation views. The trailing underscore in the package name
avoids a clash with Django's bundled `auth` app.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers `UserProfile` with Django's admin site (showing the
  user, curation permission flag, and PHI-agreement flag) and unregisters the
  built-in `Group` model since HCI does not use groups.
- `apps.py` — Django `AppConfig` for the `auth_` app.
- `backends.py` — Defines `WorkOSBackend`, a custom Django authentication
  backend that loads and refreshes a WorkOS sealed session from the
  `wos_session` cookie, and creates the corresponding `User` and `UserProfile`
  records on first login.
- `forms.py` — Defines `PHIForm`, a minimal form with a single `agree`
  checkbox used to record acceptance of the PHI agreement.
- `models.py` — Defines `UserProfile`, a one-to-one extension of Django's
  `User` model with `has_curation_permissions` and `has_signed_phi_agreement`
  flags and a `can_curate` property combining authentication and both flags.
- `permissions.py` — Provides `ProtectedViewMixin` (for class-based views) and
  the `protected_view` decorator (for function-based views), both of which
  require the user to be authenticated and to have `can_curate` evaluate to
  `True`.
- `urls.py` — URL routes for the app: `login`, `callback`, `logout`,
  `profile`, and `phi`.
- `views.py` — Function-based views for the app: `login_` (redirects to the
  WorkOS hosted login page), `callback` (handles the WorkOS auth code and sets
  the sealed-session cookie), `logout_` (clears the cookie and logs out),
  `profile` (renders the user's profile page), and `phi` (renders and processes
  the PHI agreement form).

## Subdirectories

- `migrations/` — Django database migrations for the `UserProfile` model.
- `templates/auth_/` — HTML templates for the app: `profile.html` for the user
  profile page and `phi.html` for the PHI agreement form.
