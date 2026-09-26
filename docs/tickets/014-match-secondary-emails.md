# Match Legacy Users by Secondary Email

## The Problem

On a user's first Clerk login, `ClerkBackend.authenticate` in `src/auth_/backends.py`
links the Clerk account to an existing HCI user (the WorkOS migration path) by matching
`User.username` against the Clerk account's email. Only the primary email is ever
checked:

- The `callback` view in `src/auth_/views.py` picks out the primary email from
  `clerk_user.email_addresses` and passes only that address to `authenticate()` as
  `clerk_email`. It ignores every other address on the Clerk account.
- Stage 2 of `ClerkBackend.authenticate` runs `User.objects.get(username=clerk_email)`.
  This is an exact, case-sensitive match.

Suppose an existing HCI user `bar@site.org` signs in with a Clerk account whose primary
email is `foo@site.org` and whose secondary email is `bar@site.org`. Stage 1 misses (no
profile has the Clerk ID yet), Stage 2 misses (no user named `foo@site.org`), and Stage
3 creates a new, empty `foo@site.org` user linked to the Clerk ID. The old account keeps
its curation, review, and PHI flags but is never linked. Every later login matches the
new account in Stage 1, so an admin has to fix it by hand.

The case-sensitive match causes the same problem: a stored `Foo@site.org` doesn't match
a Clerk email of `foo@site.org`.

This only affects a user's first Clerk login. Once a profile has a `clerk_user_id`,
Stage 1 matches it no matter what the emails are.

## The Technical Plan

Widen the Stage 2 lookup so it checks the primary email first and then the account's
verified secondary emails. Match case-insensitively.

Decisions:

- **Only verified secondary emails count.** Clerk lets a user add an address before
  verifying it. If unverified addresses counted, anyone could add another person's
  email to their Clerk account and take over that person's HCI account on first login.
  An address counts as verified when `email.verification.status == "verified"`. (In
  `clerk_backend_api`, `EmailAddress.verification` can be null. The `status` enums are
  `str` subclasses, so comparing to the string works.) The primary email keeps its
  current behavior.
- **The primary email wins.** If the primary email matches a user, use that user, even
  if a secondary email matches a different user.
- **Refuse to guess when secondaries disagree.** If the primary doesn't match and the
  verified secondaries match more than one distinct user, log an error that names the
  Clerk user ID and the matching usernames, and return `None`. The callback already
  redirects to login when `authenticate()` returns `None`, and an admin can resolve the
  conflict. The same applies when a single case-insensitive lookup matches more than one
  user (e.g., both `Foo@site.org` and `foo@site.org` exist).
- **Stage 3 doesn't change.** A new user is still created with the primary email as
  both `username` and `email`.
- **Keep the `clerk_email` keyword.** Add a `clerk_secondary_emails` keyword (a list of
  strings, default empty) instead of replacing `clerk_email`, so existing callers and
  tests keep working.

## Detailed Implementation

### `src/auth_/views.py` — modify

In `callback`, after resolving `primary_email`, build `secondary_emails`: the
`email_address` of every entry in `clerk_user.email_addresses` whose `id` isn't
`primary_email_address_id` and whose `verification` is non-null with status
`"verified"`. Pass it to `authenticate()` as `clerk_secondary_emails`. Log how many
verified secondary emails were found, but don't log the addresses.

### `src/auth_/backends.py` — modify

Accept `clerk_secondary_emails` from `kwargs`. In Stage 2:

1. Look up the primary email with `username__iexact`. If exactly one user matches, link
   and return it as today. If more than one matches, log an error and return `None`.
2. Otherwise, look up each verified secondary email the same way. Collect the distinct
   matching users. If exactly one user matches, link and return it, and log that the
   match came from a secondary email. If more than one matches, log an error and return
   `None`.
3. Otherwise, fall through to Stage 3.

Consider pulling the email lookup into a small private helper. Update the
`authenticate` docstring to describe the new Stage 2.

### `src/auth_/tests.py` — modify

Write these tests first.

In `ClerkBackendTest`:

- A secondary email matches an existing user: that user is returned, `clerk_user_id` is
  written to their profile, and no new user is created.
- The primary and a secondary email match different users: the primary's user is
  returned.
- The match is case-insensitive for both primary and secondary emails.
- Two secondary emails match two different users: returns `None`, logs an error,
  creates no user, and writes no `clerk_user_id`.
- A case-insensitive lookup that matches two users returns `None`.
- No email matches: a new user is created with the primary email (the existing test
  covers this; make sure it still passes with `clerk_secondary_emails` provided).

In `CallbackViewTest`, extend `_make_clerk_user` so it can build extra email objects
with a verification status. Then test that:

- Verified secondary emails are passed to `authenticate()`.
- Unverified secondary emails and emails with `verification = None` aren't passed.
- End to end, a legacy user whose username matches a verified secondary email is logged
  in as that user.

### Docs — modify

- `src/auth_/README.md`: update the `backends.py`, `views.py`, and `tests.py` entries.
- `docs/plans/005-clerk-auth.md`: add a short note that Stage 2 now also matches
  verified secondary emails case-insensitively, pointing to this ticket.

`docs/design.md` doesn't describe email matching. Its stale WorkOS text is covered by
`docs/tickets/013-stale-auth-docs.md`.

## Sources

- Found by reviewing the auth code for a user with separate primary and secondary
  emails.
