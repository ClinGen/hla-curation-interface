# Associate Users with Projects via Clerk Metadata

## The Problem

Our Clerk instance may be shared by more than one project. Mark Woon uses a `projects`
list in Clerk user metadata (for example, `metadata.projects = ["cpgx"]`) to mark which
users belong to ClinPGx. The HCI doesn't read or write this metadata today.
`ClerkBackend.authenticate` in `src/auth_/backends.py` links or creates an HCI user for
any Clerk account that signs in, and `UserProfile` in `src/auth_/models.py` has no
notion of a project.

We want HCI users tagged in Clerk the same way, so each project can tell which users
are its own. We may also want the HCI to use the tag to decide who can sign in.

This needs more planning before it can be broken down into implementation beads.

## Open Questions

1. **Which metadata?** Clerk has `public_metadata`, `private_metadata`, and
   `unsafe_metadata`. Users can edit `unsafe_metadata` themselves, so it must not
   control access. Which one does ClinPGx use, and what is the exact key and value
   format (`projects: ["cpgx"]`)?
2. **What is the HCI's project value?** For example, `"hci"`. Who else needs to agree
   on it, such as Mark Woon or other projects sharing the instance?
3. **Who sets it, and when?** Options: the HCI adds `"hci"` on a user's first login
   through the Clerk Backend API; an admin sets it in the Clerk dashboard; or a one-off
   script backfills existing HCI users. Writing it from the HCI needs a secret key with
   permission to update users. Updates must append to the list, not overwrite other
   projects' entries.
4. **Does it gate access?** Should a Clerk user without `"hci"` in `projects` be refused
   at login, created with no permissions (today's behavior), or tagged automatically?
5. **Is it the source of truth for permissions?** Should curation, review, or PHI flags
   also move into Clerk metadata, or stay on `UserProfile`?
6. **Existing users.** How do we backfill the tag for users who already have a
   `clerk_user_id`, and for legacy users who haven't signed in with Clerk yet?

## Sources

- Conversation with the user on 2026-09-25: Mark Woon uses `cpgx` in
  `metadata.projects` for ClinPGx users.
- `docs/plans/005-clerk-auth.md` describes the current Clerk integration.
