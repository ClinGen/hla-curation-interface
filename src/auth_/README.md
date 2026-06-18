# `auth_`

The `auth_` app handles authentication and user profile management for the HCI. It
integrates with WorkOS for SSO login via a custom authentication backend, extends
Django's built-in `User` model with a `UserProfile` that tracks PHI agreement and
curation permissions, and provides views for login/logout, profile inspection, PHI
agreement signing, and profile change history.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers the `UserProfile` model with the Django admin site using `SimpleHistoryAdmin`,
exposes `user`, `has_curation_permissions`, and `has_signed_phi_agreement` in the list
view, and unregisters the built-in `Group` model (which is not used by this
application).

### `apps.py`

Defines the `AuthConfig` app configuration, setting the app name to `auth_` and the
default primary-key field type to `BigAutoField`.

### `backends.py`

Implements `WorkOSBackend`, a custom Django authentication backend that authenticates
users by loading and verifying a WorkOS sealed session cookie. On successful
authentication it creates or retrieves the Django `User` and associated `UserProfile`
records, and handles session refresh when the initial authentication has expired.

### `forms.py`

Defines `PHIForm`, a simple Django `Form` with a single `CheckboxInput` field used to
record a user's agreement to the PHI terms.

### `models.py`

Defines `UserProfile`, a one-to-one extension of Django's `User` model that stores
whether the user has signed the PHI agreement and whether they have been granted
curation permissions. The `can_curate` property returns `True` only when the user is
authenticated and both flags are set; history tracking is added via `HistoricalRecords`.

### `permissions.py`

Defines `ProtectedViewMixin` (for class-based views) and the `protected_view` decorator
(for function-based views), both of which enforce that a user must be authenticated and
have `can_curate == True` to access a view, raising `PermissionDenied` otherwise.

### `templates/auth_/change.html`

Renders a detail page for a single history change record on the current user's profile,
with a breadcrumb trail from Home through Profile and Profile History, then including
the shared `common/history/change_body.html` partial.

### `templates/auth_/history.html`

Renders a page listing the full change history of the current user's profile, with a
breadcrumb trail from Home through Profile, then including the shared
`common/history/history_body.html` partial.

### `templates/auth_/phi.html`

Renders the PHI Agreement page, presenting the agreement text and a required checkbox
that the user must check before submitting to record that they have signed the
agreement.

### `templates/auth_/profile.html`

Renders the User Profile page, displaying the user's email alongside a table showing the
status of their PHI agreement and curation permissions, with contextual links to sign
the agreement or contact HCI support if either is missing.

### `urls.py`

Maps URL patterns for the auth app: `login`, `callback`, `logout`, `profile`,
`profile/history`, `profile/history/<history_id>/change`, and `phi`, each wired to the
corresponding view function.

### `views.py`

Provides function-based views for the full authentication and profile lifecycle:
`login_` redirects to WorkOS AuthKit, `callback` exchanges the OAuth code for a sealed
session cookie and logs the user in, `logout_` deletes the cookie and logs the user out,
`profile` displays the user's profile, `profile_history` and `profile_change` display
history records, and `phi` handles PHI agreement form submission.
