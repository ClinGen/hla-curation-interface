# Clerk Authentication

## The Problem

The HCI currently uses WorkOS for SSO. WorkOS handles the OAuth redirect/callback flow
and provides a sealed session cookie that the custom `WorkOSBackend` verifies at login
time. The goal is to replace WorkOS with Clerk while keeping the rest of the
authentication architecture — Django sessions, `UserProfile`, `ProtectedViewMixin`, the
PHI agreement flow — entirely unchanged. Clerk will support email/password, Google, and
Microsoft sign-in.

## The Technical Plan

The change is narrow. Only `pyproject.toml`, `src/auth_/models.py`,
`src/auth_/backends.py`, `src/auth_/views.py`, `src/auth_/tests.py`, and
`src/config/settings/base.py` need to change, plus one migration. Everything downstream
of a successful login — the Django session, `UserProfile` flags, `ProtectedViewMixin`,
`ReviewerViewMixin`, the PHI agreement flow — works identically before and after.

### Session strategy

After the callback, a standard Django session cookie is issued. The Clerk `__session`
JWT is only read once — at callback time — to identify the user and establish the Django
session. On subsequent requests, Django's session middleware handles authentication as
before. This means no per-request calls to the Clerk SDK and no changes to any view or
middleware outside `auth_`.

### User matching

`UserProfile` stores a `clerk_user_id` field (the `sub` claim from the Clerk JWT). On
every login the backend first looks up the `UserProfile` by `clerk_user_id`; if found,
that account is reused regardless of any email changes. If no match is found — which
covers all users migrating from WorkOS who have never logged in via Clerk — the backend
falls back to matching by primary email and, on success, writes the Clerk user ID into
the profile so that future logins resolve immediately by ID. If neither lookup succeeds,
a new `User` and `UserProfile` are created and the Clerk user ID is stored at that
point.

### Fetching the email

Clerk's session token (a short-lived JWT) carries the Clerk user ID (`sub`) but not
necessarily the user's email. To get the email, the callback view fetches the Clerk user
record via `clerk.users.get(user_id=sub)` immediately after verifying the token. This
adds one API call per login but keeps the JWT verification simple and requires no
customization of Clerk's JWT templates.

### Logout

The logout view calls `clerk.sessions.revoke(session_id)` to invalidate the Clerk
session server-side, then calls Django's `logout(request)` to clear the Django session
cookie. The Clerk session ID is available from the verified token payload (`sid` claim).

## Alternatives

### Verify the Clerk session on every request instead of using Django sessions

Instead of logging the user into a Django session at callback time, we could verify the
Clerk `__session` cookie in middleware on every request. This keeps Clerk as the sole
source of truth for whether a session is valid — useful if sessions need to be
invalidated instantly from Clerk's dashboard. The downside is latency: every request
incurs a JWKS-based JWT verification (fast, local) or, for revocation checking, an API
call (slower). For a small internal tool, the extra latency is acceptable, but the extra
complexity is not warranted given that the Django session approach already works
reliably and can be extended to support forced logout later if needed.

### Use Clerk's embedded sign-in component instead of the hosted page

Clerk provides a JavaScript component that renders the sign-in UI directly on the
application's login page. This gives a more seamless experience — the user never leaves
the site — and makes it easy to apply custom branding. The tradeoff is that it requires
loading Clerk's frontend JavaScript bundle and integrating it with the Django template.
Since the sign-in page is visited infrequently, the UX difference is negligible, and the
hosted page approach requires zero frontend changes.

### Include email in the Clerk JWT template

Clerk's dashboard lets you add custom claims to the session JWT, including the user's
primary email address. This would eliminate the `clerk.users.get()` API call in the
callback. The downside is that it creates an implicit dependency on a Clerk dashboard
setting that is invisible from the codebase — if the JWT template is ever reset, the
callback silently breaks. Fetching the user from the API is one extra call per login and
is explicit and self-contained in the code.

## Detailed Implementation

### Step 1 — Install the Clerk Python SDK

#### `pyproject.toml` — modify

Add `clerk-backend-api` to the `dependencies` list.

### Step 2 — Environment variables and settings

#### `.env` — modify

Remove all four WorkOS environment variables: `WORKOS_API_KEY`, `WORKOS_CLIENT_ID`,
`WORKOS_COOKIE_PASSWORD`, and `WORKOS_REDIRECT_URI`. Add `CLERK_SECRET_KEY` and
`CLERK_PUBLISHABLE_KEY` with the values from the Clerk dashboard.

#### `src/config/settings/base.py` — modify

Remove all WorkOS-related imports and settings. Read `CLERK_SECRET_KEY` and
`CLERK_PUBLISHABLE_KEY` from the environment using `os.environ` so that a missing value
raises an error at startup rather than silently passing `None` to the SDK.

Replace the `WorkOSBackend` entry in `AUTHENTICATION_BACKENDS` with
`"auth_.backends.ClerkBackend"`. Keep `"django.contrib.auth.backends.ModelBackend"` as
the second entry so that `force_login()` continues to work in tests.

Remove `SECURE_CROSS_ORIGIN_OPENER_POLICY`. The current comment explains it is needed
"for logging in with Google and Microsoft via Firebase." Firebase is no longer involved;
Clerk handles Google and Microsoft OAuth entirely on its hosted sign-in page via a
redirect flow, not a popup, so the setting is not needed.

### Step 3 — Add `clerk_user_id` to `UserProfile`

#### `src/auth_/models.py` — modify

Add a `clerk_user_id` field to `UserProfile`: a nullable, blank, unique `CharField` with
a generous `max_length` (255 is sufficient). Nullable and blank because existing users
migrating from WorkOS will not have a value until their first Clerk login. Unique
because two Django accounts must never be linked to the same Clerk identity.

#### Migration — add

Generate a migration for the new field using `uv run manage.py makemigrations`.

### Step 4 — Replace the authentication backend

#### `src/auth_/backends.py` — rewrite

Delete `WorkOSBackend` and the module-level WorkOS client and cookie-password
instantiation. Replace with `ClerkBackend`, which inherits from `ModelBackend`.

The `authenticate` method should accept `clerk_user_id` and `clerk_email` keyword
arguments and ignore all others. If `clerk_user_id` is absent, return `None`
immediately.

The lookup proceeds in two stages. First, attempt to retrieve a `UserProfile` by
`clerk_user_id`; if found, return the associated `User`. Second, if no profile has that
Clerk ID yet, attempt to retrieve a `User` by `username` matching `clerk_email` — this
covers all existing accounts that were created under WorkOS and are logging in via Clerk
for the first time. On a successful email match, write `clerk_user_id` into the profile
and save it so that all future logins for this user resolve by ID instead of falling
through to the email lookup. If neither lookup finds a match, call `get_or_create` on
`User` (with the email as both `username` and `email`) and `get_or_create` on
`UserProfile`, then set `clerk_user_id` on the new profile before returning the user.

All permission logic stays on `UserProfile` as before. Inheriting `ModelBackend` means
`has_perm` and `has_module_perms` continue to work without any additional
implementation. Keep the `get_user` method, which looks up a `User` by primary key and
returns `None` on `DoesNotExist`; this is required by Django's authentication framework
for session-based auth.

### Step 5 — Replace the auth views

#### `src/auth_/views.py` — modify

Remove the module-level WorkOS client, cookie-password, and
`seal_session_from_auth_response` import. Keep the `phi`, `profile`, `profile_history`,
and `profile_change` views entirely unchanged. Replace `login_`, `callback`, and
`logout_` as described below.

**`login_`** should build the absolute URI for the callback endpoint and redirect the
user to Clerk's hosted sign-in page, passing the callback URI as the `redirect_url`
parameter. The sign-in URL is derived from the Clerk instance's domain, which is
available from the publishable key; confirm the exact URL format against the Clerk
dashboard during implementation. The existing early-return for already-authenticated
users can be kept as-is.

**`callback`** should read the `__session` cookie from the request. If the cookie is
absent, redirect to login. Otherwise, call `verify_token` from
`clerk_backend_api.security` with the token and a `VerifyTokenOptions` instance
configured with `CLERK_SECRET_KEY`. If verification raises an exception, redirect to
login. On success, the payload contains the Clerk user ID in the `sub` claim; use it to
fetch the full user record from the Clerk API via `clerk.users.get`. Extract the primary
email address by matching `primary_email_address_id` against the user's
`email_addresses` list. If no primary email is found, redirect to login. Otherwise, call
Django's `authenticate` passing both `clerk_user_id` and `clerk_email`, call `login`
with the returned user, and redirect to `core:home`.

**`logout_`** should attempt to revoke the Clerk session before clearing the Django
session. Read the `__session` cookie, and if present, verify it to extract the `sid`
claim, then call `clerk.sessions.revoke` with that session ID. Wrap the entire Clerk
interaction in a try/except so that a stale or already-invalid token does not block the
user from being logged out. Regardless of whether Clerk revocation succeeds, call
Django's `logout` and redirect to the login page.

### Step 6 — URL patterns

#### `src/auth_/urls.py` — no changes required

The existing URL patterns (`login`, `callback`, `logout`, `profile`, `phi`, etc.) map to
the same view function names. No URL changes are needed.

### Step 7 — Remove the WorkOS SDK

#### `pyproject.toml` — modify

Remove `"workos~=8.0"` from the `dependencies` list. Verify that no other file in the
codebase imports from `workos` before removing.

### Step 8 — Tests

#### `src/common/tests.py` — no changes required

`ProtectedViewTestMixin` creates test users and calls `client.force_login()`, which
bypasses the authentication backend entirely. All existing access-control tests continue
to work as-is. `ModelBackend` (the second entry in `AUTHENTICATION_BACKENDS`) handles
`force_login()`.

#### `src/auth_/tests.py` — modify

Add new tests for the `callback` view and the `ClerkBackend` lookup logic:

- Success path: mock `verify_token` to return a valid payload and mock `clerk.users.get`
  to return a user with a primary email; assert that a Django session is established and
  the response redirects to `core:home`.
- Missing cookie: assert that a request to `callback` with no `__session` cookie
  redirects to `auth_:login`.
- Invalid token: mock `verify_token` to raise an exception; assert redirect to
  `auth_:login`.
- New user: assert that a `User` and `UserProfile` are created when neither a matching
  `clerk_user_id` nor a matching email exists, and that `clerk_user_id` is populated on
  the new profile.
- Existing user matched by Clerk ID: assert that an existing `User` and `UserProfile`
  are reused when `clerk_user_id` matches, and that no duplicate account is created.
- WorkOS migration path: assert that an existing user whose profile has no
  `clerk_user_id` is matched by email, that `clerk_user_id` is written to their profile,
  and that their existing permission flags are not overwritten.
