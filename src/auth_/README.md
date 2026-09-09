# `auth_`

This Django app handles authentication and authorization for the HLA Curation Interface using Clerk as the identity provider. It defines the `UserProfile` model that extends Django's built-in `User` with curation and PHI agreement flags, a custom Clerk authentication backend, and permission mixins and decorators used throughout the project. The directory is named `auth_` with a trailing underscore to avoid shadowing Python's built-in `auth` module.

### `__init__.py`

Empty file that marks `auth_` as a Python package.

### `admin.py`

Registers `UserProfile` with the Django admin site using `SimpleHistoryAdmin` so that staff can view and edit user profiles (including curation permissions, PHI agreement status, and Clerk user IDs) with change-history support. Also unregisters the built-in `Group` model, which is not used by this project.

### `apps.py`

Defines the `AuthConfig` app configuration class, which sets the app name to `auth_` and specifies `BigAutoField` as the default primary key type.

### `backends.py`

Implements `ClerkBackend`, a custom Django authentication backend that authenticates users via a Clerk user ID rather than a username and password. Authentication proceeds in three stages: match an existing `UserProfile` by Clerk ID, fall back to matching a legacy WorkOS user by email (migration path), or create a new `User` and `UserProfile` if no match is found.

### `forms.py`

Defines `PHIForm`, a simple form containing a single checkbox used to capture the user's agreement to the PHI (protected health information) policy.

### `js/callback.jsx`

A minimal React component that mounts a `ClerkProvider` and waits for Clerk to finish its token exchange (e.g., `__clerk_db_jwt` or `__clerk_handshake`). Once Clerk reports that it is loaded, the component redirects the browser to `/auth/callback` so the Django callback view can verify the now-set `__session` cookie.

### `js/sign-in.jsx`

Renders Clerk's embedded `SignIn` widget inside a `ClerkProvider`. If the user is already signed in when the page loads, it immediately redirects to `/auth/callback`; otherwise it displays the sign-in widget, which redirects to the same callback URL upon successful authentication.

### `models.py`

Defines `UserProfile`, a one-to-one extension of Django's `User` model that stores curation permissions (`has_curation_permissions`), PHI agreement status (`has_signed_phi_agreement`), EP reviewer permissions (`has_review_permissions`), and the associated `clerk_user_id`. Includes `can_curate` and `can_review` computed properties and tracks full change history via `django-simple-history`.

### `permissions.py`

Provides four reusable permission primitives: `ProtectedViewMixin` and `protected_view` enforce that the user has curation permissions (authenticated + PHI signed + curation flag set), while `ReviewerViewMixin` and `reviewer_view` additionally require the EP reviewer flag. The mixin variants are for class-based views and the decorator variants are for function-based views.

### `templates/auth_/callback.html`

A bare-bones HTML page (no base layout) that mounts the `clerk-callback` React component and passes the Clerk publishable key via a data attribute. It exists solely to load `callback.js` and trigger the Clerk token exchange before the browser is redirected back to the Django callback view.

### `templates/auth_/change.html`

Displays the details of a single historical change to the current user's `UserProfile`, including the change type icon and timestamp in a breadcrumb trail. Delegates the diff rendering to the shared `common/history/change_body.html` partial.

### `templates/auth_/history.html`

Shows a paginated table of all historical changes to the current user's `UserProfile`, with breadcrumb navigation back to the profile page. Delegates the table rendering to the shared `common/history/history_body.html` partial.

### `templates/auth_/login.html`

Extends the base layout and renders the `clerk-sign-in` div that the `sign-in.jsx` React component targets. Passes the Clerk publishable key as a data attribute and loads the compiled `sign-in.js` bundle.

### `templates/auth_/phi.html`

Presents the PHI agreement form with a required checkbox. On submission the view marks `has_signed_phi_agreement` on the user's profile; a Cancel link returns the user to their profile page without changes.

### `templates/auth_/profile.html`

Displays the current user's profile information, including PHI agreement status and curation permissions, each shown with a colored icon and contextual call-to-action (e.g., a link to sign the PHI agreement or an email address to request curation access). Also provides a button to navigate to the profile change-history page.

### `tests.py`

Contains unit and integration tests covering the `can_review` property on `UserProfile`, the `ReviewerViewMixin` permission enforcement, the three-stage `ClerkBackend.authenticate` logic (no ID, new user, existing-by-Clerk-ID, WorkOS migration), and the `callback` view (successful login, missing cookie, invalid token, missing primary email).

### `urls.py`

Maps the `auth/` URL prefix to the app's six views: `login`, `callback`, `logout`, `profile`, `profile/history`, `profile/history/<id>/change`, and `phi`.

### `views.py`

Implements all request-handling logic for the `auth_` app. `login_` renders the Clerk sign-in page; `callback` verifies the Clerk `__session` JWT, resolves the user's primary email via the Clerk API, calls the custom backend to find or create the Django user, and establishes a Django session; `logout_` revokes the Clerk session server-side before clearing the Django session; `profile`, `profile_history`, and `profile_change` render the user's profile and its `django-simple-history` audit trail; and `phi` handles the PHI agreement form submission.
