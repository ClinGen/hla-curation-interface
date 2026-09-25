# Stale Authentication Docs and Project Metadata

## The Problem

The HCI moved from WorkOS to Clerk in commit ce8ef5f (see
`docs/plans/005-clerk-auth.md`), but some docs still describe WorkOS as the auth
provider. A reader, or an agent, who trusts these docs will look for a
`WorkOSBackend` and a WorkOS OAuth callback that no longer exist:

- `docs/design.md` lists WorkOS as the SSO provider in the external systems section,
  lists "WorkOS + custom `WorkOSBackend`" in the stack summary, and says all views
  except login and "the WorkOS OAuth callback" are protected.
- `src/README.md` says the `auth_` app integrates "with WorkOS for hosted login".

`pyproject.toml` has two small leftovers too:

- `readme = "README.rst"`, but the file is `README.md`.
- A `[tool.django-stubs]` section from when the project type-checked with mypy. The
  project switched to ty in commit 2a89a65. The `django-stubs` dependency may still be
  useful to ty for Django types, so only the mypy plugin configuration is suspect.

`src/auth_/README.md` mentions WorkOS on purpose. `ClerkBackend` still has a migration
path that matches legacy WorkOS users by email, so those mentions are accurate.

## The Technical Plan

Update the stale passages to describe Clerk, following `docs/plans/005-clerk-auth.md`
and the current code in `src/auth_/`. Fix the `readme` key. Remove
`[tool.django-stubs]` only after confirming that nothing reads it (`ty` doesn't use
it; check the justfile and CI workflows).

## Detailed Implementation

### Step 1 — Docs

#### `docs/design.md` — modify

Replace the WorkOS entry in the external systems section with Clerk: users sign in
through the embedded Clerk widget, and the `callback` view verifies the Clerk session
token and logs the user in with a Django session. Change the stack line to
"Clerk + custom `ClerkBackend`". In "Authentication and Authorization", replace "the
WorkOS OAuth callback" with the Clerk callback view's name from `src/auth_/urls.py`.

#### `src/README.md` — modify

Change the `auth_/` description to say it integrates with Clerk.

### Step 2 — Project metadata

#### `pyproject.toml` — modify

Set `readme = "README.md"`. Remove `[tool.django-stubs]` if nothing uses it. Run
`just ci` to confirm that type checking still passes.

## Sources

- Found while writing `docs/tickets/011-settings-cruft.md`.
