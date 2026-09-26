# Review What the Django Admin Shows and Searches

## The Problem

Each app registers its models in `admin.py`, but the `list_display`, `search_fields`,
and `list_filter` choices were set model by model without a shared idea of what admins
actually do in the admin. Some choices look wrong:

- `CurationAdmin.search_fields` in `src/curation/admin.py` is `["allele", "haplotype"]`,
  and `EvidenceAdmin.search_fields` is `["publication"]`. These are foreign keys, and
  Django can't run an `icontains` search on a foreign key directly, so searching these
  lists is likely to raise an error. They probably need `allele__name`,
  `haplotype__name`, `publication__pubmed_id`, and so on.
- `AlleleAdmin` searches only `car_id`, not `name`.
- No admin searches by HCI ID (`slug`), which curators use to refer to records.
- `PublishedCurationAdmin` in `src/repo/admin.py` has no search or filters.
- `UserProfileAdmin` in `src/auth_/admin.py` should be checked for searching by email,
  username, and `clerk_user_id`, and filtering by the permission flags.

## Open Questions

1. **What do admins use the admin for?** For example: fixing user permissions, finding a
   curation someone reported by C number, correcting a mistyped Mondo ID or PMID, or
   undoing a bad status change. The answer decides what each list shows first.
2. **What should each model's list show?** Which columns (`list_display`), in what
   order, and which link to the change page?
3. **What should be searchable?** For each model, which fields, including related
   fields such as allele name, disease name, Mondo ID, PMID, and user email?
4. **What should be filterable?** For example, status, curation type, classification,
   expert panel, and permission flags.
5. **What should be read-only?** Should admins be able to edit fields that the app
   normally controls, such as `slug`, `status`, `score`, and published records?
6. **Does plan 009 change this?** If the URL and ID scheme changes
   (`docs/plans/009-stable-ids.md`), search should use the new IDs.

## Sources

- Conversation with the user on 2026-09-25.
- The current `admin.py` files in each app.
