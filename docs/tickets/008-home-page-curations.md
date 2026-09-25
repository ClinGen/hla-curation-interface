# Home Page "Your Curations" Table

## The Problem

For logged-in users, the home page shows a "Your Curations" table. The `home` view in
`src/core/views.py` builds it as
`CurationTable(request.user.curations_added.all())` and configures it with
`RequestConfig`. Two things are wrong:

1. **The table shows even when the user has no curations.** `core/home.html` guards
   the section with `{% if user.is_authenticated and curation_table %}`, but a
   django-tables2 `Table` defines neither `__bool__` nor `__len__`, so the table object
   is always truthy. Users with no curations see a "Your Curations" heading over an
   empty table.
2. **The table isn't sorted by most recent.** The queryset has no `order_by`, and
   `Curation.Meta` has no `ordering`, so rows come back in database order (in practice,
   oldest first). The main curation list (`CurationList` in `src/curation/views.py`)
   already uses `ordering = ["-updated_at"]`, and commit 10287d5 applied the same
   ordering to every list view, but the home page table was missed.

The goal: hide the section entirely when the user has no curations, and otherwise
sort it by `updated_at` descending. Clicking a column header should still work.

## The Technical Plan

In `home`, build the queryset as
`request.user.curations_added.order_by("-updated_at")`. Add the table to the context
only if `queryset.exists()`, so the existing template guard works as intended. Keep
`RequestConfig(request).configure(table)` so the column headers stay sortable. When a
`?sort=` parameter is present it overrides the default order, and when it is absent
the queryset order is used.

## Detailed Implementation

### Step 1 — Hide when empty, sort by most recent

#### `src/core/tests.py` — modify

Write these tests first in a new `HomeCurationTableTest` (log in with a user that has
a `UserProfile` with PHI and curation permissions, as in `AccountActivationMessageTest`,
and load the `test_alleles.json` and `test_diseases.json` fixtures):

- A user with no curations: `curation_table` is not in `response.context`, and the
  response doesn't contain "Your Curations".
- A user with curations: "Your Curations" appears, and only that user's curations are
  listed (another user's curation slug is absent).
- Ordering: create two curations, then set explicit `updated_at` values with
  `Curation.objects.filter(pk=...).update(updated_at=...)` (because `auto_now`
  overrides values set through `save()`), making the older curation the most recently
  updated. The rows in `response.context["curation_table"].rows` come back most
  recently updated first.

#### `src/core/views.py` — modify

Change `home` as described in the plan. Update its docstring to mention the sorting
and the empty case.

#### `src/core/templates/core/home.html` — modify

No logic change is required. Optionally simplify the guard to
`{% if curation_table %}`, because the view only sets it for authenticated users with
curations.

#### `src/core/README.md` — modify

Update the `views.py` and `templates/core/home.html` entries to say that the table is
sorted by most recently updated and hidden when the user has no curations.

## Sources

- Notes: "HCI: If you don't have curations, don't show table on home page"
- Notes: "HCI: If you have curations, sort by most recently modified"
- Notes: "HCI: Sort 'Your Curations' by most recent"
