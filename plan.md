# Plan: Replace WorkOS with Clerk

## Context

The app currently uses WorkOS AuthKit for authentication via a custom `WorkOSBackend` in
`src/auth_/backends.py`. The backend does just-in-time (JIT) provisioning: on every
request, it validates the WorkOS sealed session cookie and does `get_or_create` on a
Django `User` keyed by email, plus a companion `UserProfile` row that carries
app-specific flags (`has_curation_permissions`, `has_signed_phi_agreement`).

Authorization is entirely Django-side: `ProtectedViewMixin` and the `protected_view`
decorator in `src/auth_/permissions.py` gate access on
`request.user.profile.can_curate`.

The goal is to swap WorkOS for Clerk while keeping this structure intact. The Django
side already expresses the architecture we want — only the identity provider changes.

## Architectural decisions

- **Keep Django `User` as a thin FK target.** Don't abandon `auth_user`. Clerk owns
  identity; Django owns one thin row per user keyed on `clerk_id`, plus the existing
  `UserProfile`. Skipping the row would mean losing Django admin, FK ergonomics, and
  ecosystem packages — a much larger blast radius than any sync savings.
- **No frontend rewrite.** Clerk integration alone does not justify moving to React. Use
  Clerk's hosted Account Portal for sign-in/sign-up, mirroring how AuthKit is used
  today.
- **One shared Clerk Application across the company** (confirmed with coworkers). No
  per-app isolation at the Application level; API keys and session-token claim shape are
  shared.
- **Assume flat orgs for now.** The wider organization has not yet decided between
  granular (one Clerk Organization per app) and flat (one or few large Organizations).
  Assume flat; upgrading to granular later is additive (a nullable `clerk_org_id` on
  `UserProfile` and a filter in the backend), not a rewrite.
- **No webhooks.** JIT-only, matching current WorkOS behavior. Webhooks are not cleanly
  scopable in a shared Application without Organizations — every team's `user.*` events
  would land on one endpoint.
- **Django owns authorization.** Clerk answers "who are you";
  `UserProfile.has_curation_permissions` and `has_signed_phi_agreement` continue to
  answer "what can you do," managed by admins through Django admin. Being authenticated
  via Clerk only proves company membership, not curation entitlement.
- **Switch the stable identifier to `clerk_id`.** Today `User.username = email`. Clerk
  users can change their email; keying on `clerk_id` (stored on `UserProfile`) is
  durable.

## What does not change

- All seven `AUTH_USER_MODEL` foreign-key migrations across `allele`, `curation`,
  `disease`, `haplotype`, `publication`, `repo`, and `auth_`.
- Every `form.instance.added_by = self.request.user` pattern in views.
- `UserProfile` model, `can_curate` property, PHI agreement flow.
- `ProtectedViewMixin`, `protected_view` decorator.
- Django admin.
- Database schema, other than a new `clerk_id` column on `UserProfile`.

## Phased plan

### Phase 1 — Add Clerk backend alongside WorkOS

No cutover. Both auth systems live at different URLs and are exercised in parallel in
dev.

1. Add a Clerk JWT verification dependency to `pyproject.toml` (`clerk-backend-api`).
2. Create `src/auth_/clerk_backend.py` with a `ClerkBackend(BaseBackend)` class
   mirroring `WorkOSBackend.authenticate`: read the Clerk session cookie/JWT, verify
   against Clerk's JWKS, `get_or_create(User)`, and
   `get_or_create(UserProfile, defaults={"clerk_id": ...})`.
3. Add `clerk_login`, `clerk_callback`, `clerk_logout` views in `src/auth_/views.py`
   next to the existing WorkOS views.
4. Wire Clerk URLs at `/auth/clerk/login`, `/auth/clerk/callback`, `/auth/clerk/logout`
   in `src/auth_/urls.py`. Leave `/auth/login` untouched for now.
5. Append `auth_.clerk_backend.ClerkBackend` to `AUTHENTICATION_BACKENDS` in
   `src/config/settings/base.py`.
6. Add a settings flag `AUTH_PROVIDER = "workos" | "clerk"` so the eventual cutover is
   config-driven.
7. Add Clerk env vars (`CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, JWKS URL or signing
   key) to `.env` and document them.

### Phase 2 — Schema for the stable identifier

1. Add `clerk_id = CharField(max_length=64, unique=True, null=True, blank=True)` to
   `UserProfile`.
2. Generate and run the migration.
3. In `ClerkBackend.authenticate`, resolve the user in this order:
   - Try `UserProfile.objects.get(clerk_id=...)`, return that user.
   - Fall back to `User.objects.get(email=...)` for users pre-existing from WorkOS, then
     stamp `clerk_id` onto their profile.
   - If neither exists, create both rows with `clerk_id` populated.

This handles existing accounts on their first post-cutover login without needing a bulk
backfill.

### Phase 3 — Test in parallel

1. In dev, exercise both login flows. Confirm the same user ends up as the same `User`
   row whether they log in via WorkOS or Clerk (the email fallback in Phase 2 guarantees
   this for pre-existing users).
2. Verify `ProtectedViewMixin` and `protected_view` still gate correctly when
   `request.user` came from Clerk.
3. Verify `form.instance.added_by = self.request.user` writes still work.
4. Verify Django admin still lists and edits users normally.
5. Run `just py-format`, `just py-lint`, `just py-type-check`, and `just test-all`.
   Existing tests should pass unchanged — the Django-side contract is identical.

### Phase 4 — Cutover

1. Flip `AUTH_PROVIDER` to `"clerk"` in prod settings.
2. Change `LOGIN_URL` in `src/config/settings/base.py` to `/auth/clerk/login`.
3. Update template links pointing to `/auth/login` (or add a redirect).
4. Audit the landing page and any "logged-in but not curator" views for graceful
   degradation. JIT provisioning will create `has_curation_permissions=False` rows for
   anyone at the company who tries to log in — these users should see a clear "awaiting
   admin approval" state rather than broken or empty curation UI.
5. Document for admins: when someone leaves the HLA team but stays at the company, Clerk
   will not signal it — an admin must flip `has_curation_permissions` to `False` in
   Django admin. This matches current WorkOS behavior.
6. Leave WorkOS code in place for one release cycle as a rollback path.

### Phase 5 — Remove WorkOS

Only after the cutover has been stable in prod.

1. Remove `WorkOSBackend` from `AUTHENTICATION_BACKENDS`.
2. Delete `WorkOSBackend` from `src/auth_/backends.py` (or delete the file if nothing
   else remains).
3. Delete the WorkOS login/callback/logout views and URLs.
4. Remove the `workos` dependency from `pyproject.toml`.
5. Remove `WORKOS_*` env vars from `.env` and any deployment configs.
6. Once `clerk_id` is populated for every active profile (a spot-check query is enough),
   make the field `null=False` via migration.

## Open items

- **Clerk Organizations decision at the org level.** If the wider org later chooses
  granular Organizations (one per app), revisit: add `clerk_org_id` to `UserProfile`,
  filter authentication by Org membership, and optionally subscribe to
  `organizationMembership.created` / `.deleted` webhooks for a cleaner provisioning
  signal. Additive; does not invalidate this plan.
- **`username` backfill for pre-WorkOS users.** The Phase 2 fallback handles login
  correctly, but existing rows keep `username = email`. A later backfill to switch
  `username` to `clerk_id` would be cleaner but is not required.
- **Session token customization.** Anything added to Clerk's session JWT is shared
  across every app in the Application. If custom claims become useful (e.g.,
  `app: "hla-curation"`), coordinate with whoever owns the shared Application.

## Reference

- [Multi-tenant architecture — How Clerk works](https://clerk.com/docs/guides/how-clerk-works/multi-tenant-architecture)
- [Organizations — Build multi-tenant B2B applications](https://clerk.com/docs/guides/organizations/overview)
- [Manage your workspace — Clerk Dashboard](https://clerk.com/docs/guides/dashboard/overview)
- [Instances / Environments — Development](https://clerk.com/docs/guides/development/managing-environments)
- [Clerk Pricing](https://clerk.com/pricing)
