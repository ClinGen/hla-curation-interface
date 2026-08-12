# Expert Panel Review

## The Problem

Today, any curator with curation permissions can publish a finished curation to the
public HLA repository with a single click. There is no review step between a curator
completing their work and that work becoming publicly visible. This means the
authoritative HLA-disease classifications in the repository reflect individual curator
judgment rather than the consensus of the expert panel that is supposed to govern them.
It also means there is no mechanism for updating a published curation when new evidence
emerges or an earlier assessment needs to be revised.

## The Technical Plan

The changes fall into three areas: a new curation lifecycle, an EP review step that sits
in the middle of that lifecycle, and a forking mechanism that allows published curations
to be updated over time. Here is how the full picture fits together:

```
  [In Progress]
       |
       |  submit for review
       v
  [Ready for Review] --> [Review Form]
       ^                      |
       |    needs revision    |  approved
       +----------------------+
                              |
                              v
                       [Provisional]
                              |
                              |  publish
                              v
                       [Published] -------------> [Visible in HLArepo]
                              |                      ^
                              |  fork                | supersedes
                              v                      |
                       [In Progress] ----------------+
```

### The curation lifecycle

A curation now moves through four states instead of two. While it is **In Progress** the
curator is actively adding and editing evidence records. When they are done, they submit
it for review, which moves it to **Ready for Review** and locks it — no further edits
are possible until the expert panel acts. If the panel approves, the curation moves to
**Provisional**, where it stays locked but is now eligible for publication. A curator
with the correct permissions can publish it, moving it to **Published**, at which point
it is permanently read-only. If the panel sends it back, it returns to In Progress and
the curator can edit it again; the panel's notes are retained so the curator can see the
reason for the rejection.

### Classification

Classification now has two layers. A suggested classification is computed automatically
from the curation's total score and displayed throughout the workflow as a reference
point — it requires no input from anyone. The authoritative classification is set by the
EP reviewer at approval time. The reviewer must choose it explicitly and provide written
notes explaining the panel's reasoning, even if they are simply confirming the
suggestion. Before the panel acts, only the suggestion is shown; after approval, the
EP's classification replaces it everywhere.

### Expert panel review

A small number of users are designated as EP reviewers via the admin. They are ordinary
curators with an extra permission flag. When a curation reaches Ready for Review, only
those users see a Review button. The review page shows a read-only summary of the
curation — its score, the suggested classification, and all evidence — so the reviewer
has the context they need. They then record the panel's decision: approve (choosing a
classification, providing notes, and recording the expert panel by its five-digit
numeric ID) or send back for revision. The reviewer is a proxy recording an outcome that
the panel reached outside the system.

For now, all users are assumed to belong to the generic HLA Curation Taskforce, so the
panel ID field is pre-populated with that ID and requires no input. In a future update,
users will be associated with one or more specific expert panels, and the review form
will let them select the relevant panel from that list rather than entering an ID
manually.

### Forking and the repository

Once a curation is published it cannot be edited. If a curator needs to update it —
because new evidence has emerged, data was incorrect, or the panel's assessment has
changed — they fork it. Forking creates a new curation with all evidence records carried
over from the published one, and goes through the full lifecycle again: editing, review,
approval, publication. When the fork is published, it supersedes the original. The
public repository keeps both versions visible but marks the older one as superseded and
links forward to the current one, so the full history of a curation is always navigable.

## Alternatives

### Keeping expert panel fields visible after a rejection

When the panel sends a curation back for revision, the plan retains all EP fields so the
curator can see the reason for the rejection on the curation detail page. An alternative
was to clear those fields on revert, on the assumption that curators are closely enough
involved in EP proceedings that they already know the reason. We also considered a
middle path: keep the fields intact while the curation is In Progress, then clear them
when the curator re-submits, so the next reviewer always starts fresh. Ultimately we
retained the fields because surfacing the panel's notes inside the system is useful even
when the curator already knows the outcome informally.

### Snapshot-based versioning

One approach to supporting updated curations was to take a snapshot of a curation's
complete state — all fields and evidence — at the moment of publication, and store that
snapshot so historical versions could be reconstructed exactly. This would have made
`PublishedCuration` a much heavier record. A lighter variant was to rely on
django-simple-history to reconstruct past states on demand. Both approaches were set
aside in favor of the fork model, which gets the same result more naturally: because a
fork is a new `Curation` record, each published version is already a self-contained,
independent object. No snapshot logic or history reconstruction is needed.

### Versioned `PublishedCuration` records

A related idea was to change `PublishedCuration` from a one-to-one wrapper to a
one-to-many relationship, so a single `Curation` could accumulate multiple published
versions over time, each with a version number. This was ruled out because it conflates
two things that should be separate: the curation (a specific allele-disease pairing and
its evidence) and a revision to that curation (which is substantively different work
that warrants its own record). The fork model keeps these separate cleanly.

### Dedicated status-transition timestamp fields

The original plan added four `DateTimeField` columns (`in_progress_at`,
`ready_for_review_at`, `provisional_at`, `published_at`) to be stamped by the relevant
view at each transition. These were removed in favor of relying on
`django-simple-history`, which already records every field change together with a
timestamp on every save. Separate columns create a second source of truth for the same
information, with no mechanism to stay in sync if status changes outside the normal view
paths (admin, shell, tests). When the timestamp for a given transition is needed, it can
be derived from the history record where `status` changed to that value.

### Storing a superseded flag

Rather than inferring supersession by following the fork chain, we considered adding a
boolean `superseded` flag directly to `PublishedCuration` that would be set when a fork
is published. This would make queries simpler. We chose inference instead because a
stored flag is another piece of state that can drift out of sync — if a fork is
published and the flag update fails, the repository is in an inconsistent state. The
fork chain is the ground truth and supersession falls out of it for free.

### Requiring criteria for the definitive classification

`DEFINITIVE` is the highest possible classification and is not reachable via the
automatic suggestion logic — it can only be chosen by the reviewer as an explicit
override. We discussed whether the system should enforce specific criteria for when
definitive is appropriate, such as a minimum score threshold or a checklist. This was
ruled out in favor of leaving it to the panel's discretion. The required notes field
ensures the reviewer always explains their reasoning, which is the meaningful
accountability mechanism here.

## Detailed Implementation

The steps below are ordered by dependency. Each step can be implemented and committed
independently; later steps reference constants, models, and helpers introduced by
earlier ones.

### Step 1 — Status constants

#### `src/curation/constants/models/common.py` — modify

`Evidence.status` still uses `Status.DONE` (curators mark individual evidence records as
Done before submitting a curation for review), so `DONE` must be kept. Do not remove it
from `Status`.

Add three new constants following the existing 3-character uppercase code convention:
`READY_FOR_REVIEW = "RFR"`, `PROVISIONAL = "PRO"`, and `PUBLISHED = "PUB"`.

Split the single shared `STATUS_CHOICES` dict into two:

- `STATUS_CHOICES` — keep as-is (`IN_PROGRESS` + `DONE`); still used by
  `Evidence.status`.
- `CURATION_STATUS_CHOICES` — new dict containing `IN_PROGRESS`, `READY_FOR_REVIEW`,
  `PROVISIONAL`, and `PUBLISHED`; used by `Curation.status` instead of `STATUS_CHOICES`.

Also add `CURATION_STATUS_TRANSITIONS`, a module-level dict mapping each curation status
to the `frozenset` of statuses it may legally transition to. This is the single source
of truth for the state machine and is imported by the `Curation` model.

Update `Curation.status` in `src/curation/models.py` to use `CURATION_STATUS_CHOICES`
and update its `max_length` if needed (current value is 3, which fits all codes). Leave
`Evidence.status` unchanged — it keeps `STATUS_CHOICES` and `max_length=3`.

This is the first change because every subsequent file that references a curation status
value depends on these constants existing.

### Step 2 — EP permissions

#### `src/auth_/models.py` — modify

Add `has_review_permissions = models.BooleanField(default=False)` to `UserProfile`. Add
a `can_review` property that returns `self.has_review_permissions and self.can_curate` —
EP reviewers are a strict subset of users who also hold curation permissions.

#### `src/auth_/admin.py` — modify

Add `has_review_permissions` to the `UserProfile` admin's `list_display` and `fields`.
This checkbox is the only mechanism for designating EP reviewers.

#### `src/auth_/permissions.py` — modify

Add `ReviewerViewMixin` (for class-based views) and the `reviewer_view` decorator (for
function-based views). Both return 403 unless `request.user.userprofile.can_review` is
`True`. The implementation mirrors the existing `ProtectedViewMixin` / `protected_view`
pair.

### Step 3 — Model changes

#### `src/curation/models.py` — modify

*Remove:*

- The `classification` `CharField` and its validator reference. Classification is no
  longer curator-controlled.

*Add — EP review fields* (all `null=True, blank=True`; retained when a curation is
reverted to `In Progress` so the curator can see the rejection reason):

- `ep_classification = models.CharField(max_length=3, choices=CLASSIFICATION_CHOICES, null=True, blank=True)`
- `ep_evidence_summary = models.TextField(null=True, blank=True)`
- `ep_additional_notes = models.TextField(null=True, blank=True)`
- `ep = models.CharField(max_length=5, null=True, blank=True)` — five-digit numeric ID
  identifying the expert panel or affiliation

*Add — lineage:*

- `forked_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forks')`

*Add — `suggested_classification` property:*

```python
@property
def suggested_classification(self):
    s = self.score
    if s == 0:
        return None
    elif s < 25:
        return Classification.LIMITED
    elif s <= 50:
        return Classification.MODERATE
    else:
        return Classification.STRONG
```

*Add — lifecycle methods:*

- `CURATION_STATUS_TRANSITIONS` — imported from `constants/models/common.py`; see Step
  1\.
- `is_locked` — property returning `True` when `status` is `READY_FOR_REVIEW`,
  `PROVISIONAL`, or `PUBLISHED`.
- `can_submit()` — returns a list of human-readable error strings; an empty list means
  the curation is ready to submit. Runs all pre-submit checks (status, included
  evidence, evidence done, `needs_review` cleared) using a queryset `filter` rather than
  a Python list comprehension.
- `transition_to(new_status)` — validates the move against `CURATION_STATUS_TRANSITIONS`
  and raises `ValueError` on an illegal transition, then sets `status` and saves.

*Add — `Evidence.copy_to(curation, added_by=None)`:*

Returns a new `Evidence` instance with all field values copied, bound to `curation`.
Re-adds the `demographics` M2M relation. Moves the deep-copy logic out of the fork view
and onto the model so that adding a new `Evidence` field requires only one place to
update.

*Fix — `Curation.disease`:*

Change `null=True` to `null=False`. `blank=False` was already set; allowing a DB NULL
contradicted it and permitted disease-less curations to be created via the shell, admin,
or fixtures.

### Step 4 — Migrations

Use Django to create migrations instead of creating them manually.

### Step 5 — Validators

#### `src/curation/validators/models/curation.py` — modify

- Delete `validate_classification` entirely. The curator no longer sets classification,
  so there is nothing to validate on the model side.
- Update `validate_status`: change the guarded status from `Status.DONE` to
  `Status.READY_FOR_REVIEW`. The same evidence-completeness check (all included evidence
  must have status `Done`) now gates the Submit for Review transition instead of the old
  Done transition.

### Step 6 — Forms

#### `src/curation/forms.py` — modify

- Remove `classification` from `CurationEditForm.Meta.fields`. The curator can no longer
  set it.

- Add `EPReviewForm`, a plain `forms.Form` with five fields:

  - `decision` — `ChoiceField` with choices `needs_revision` / `approved`; drives view
    logic but is not persisted as a model field
  - `ep_classification` — `ChoiceField` drawing from `CLASSIFICATION_CHOICES`
  - `ep_evidence_summary` — `CharField` with `Textarea` widget
  - `ep_additional_notes` — `CharField` with `Textarea` widget, `required=False`
  - `ep` — `ChoiceField` rendered as a `<select>`; currently contains a single option:
    the generic HLA Curation Taskforce ID. In a future update the choices will be
    populated from the expert panels associated with the reviewer's user account.

`clean()` enforces that `ep_classification`, `ep_evidence_summary`, and `ep` are
non-empty when `decision == "approved"`. When `decision == "needs_revision"` these
fields are optional — the reviewer may leave them blank, in which case the view stores
`None`; any previously-set EP values are retained if the reviewer leaves the fields
populated.

### Step 7 — Views

#### `src/curation/views.py` — modify

*Locking changes:*

The locking check appears in `curation_edit_evidence`, `EvidenceCreate`, and
`EvidenceEdit`. All three use `curation.is_locked` (the model property) rather than an
inline status tuple, eliminating a three-site duplication. (`CurationEdit` was removed
in Step 15.)

*`curation_publish` — modify:*

Calls `curation.transition_to(Status.PUBLISHED)` inside `transaction.atomic()`, with
`PublishedCuration` creation inside the same block. `transition_to` enforces the
`PROVISIONAL → PUBLISHED` guard and raises `ValueError` if the curation is in any other
state, which the view catches and converts to an error message. Redirects to
`repo-detail` on success.

*`curation_submit` — new:*

A `@protected_view` POST-only function. Delegates all pre-submit validation to
`curation.can_submit()`, which returns a list of error strings. If the list is
non-empty, all errors are surfaced as messages and the view redirects back to the detail
page. On success, calls `curation.transition_to(Status.READY_FOR_REVIEW)` and redirects
with a success message.

*`curation_review` — new:*

A `@reviewer_view` GET/POST function. GET renders `curation/review.html` with a fresh
`EPReviewForm` pre-populated with any existing EP fields. POST validates `EPReviewForm`,
sets all four EP fields on the curation object, then branches on `decision`:

- `needs_revision`: calls `curation.transition_to(Status.IN_PROGRESS)`, which saves all
  dirty fields (including the EP notes) in a single write. EP fields are retained so the
  curator can see the rejection reason.
- `approved`: calls `curation.transition_to(Status.PROVISIONAL)`, again saving
  everything in one write.

Both paths redirect to the curation detail page.

*`curation_fork` — new:*

A `@protected_view` POST-only function. Verifies that
`source.status == Status.PUBLISHED`, returning 400 if not. Wraps the entire fork in
`transaction.atomic()` so a partial failure (e.g., an exception mid-loop) rolls back
both the new `Curation` and any partially-created `Evidence` records. Creates a new
`Curation` with `forked_from=source`, then iterates over
`source.evidence.prefetch_related("demographics").all()` calling `evidence.copy_to()`
for each record. Redirects to the new curation's detail page.

### Step 8 — URLs

#### `src/curation/urls.py` — modify

Add three new routes:

```
<slug:curation_slug>/submit  →  curation_submit   name: curation-submit
<slug:curation_slug>/review  →  curation_review   name: curation-review
<slug:curation_slug>/fork    →  curation_fork     name: curation-fork
```

### Step 9 — Curation templates

#### `src/curation/templates/curation/partials/buttons.html` — modify

Replace the current static button set with status-dependent rendering:

- `IN_PROGRESS` — Edit, Edit Evidence, Submit for Review
- `READY_FOR_REVIEW` (EP reviewer) — Review
- `READY_FOR_REVIEW` (non-EP curator) — Locked notice; no action buttons
- `PROVISIONAL` — Publish to HLA Repo
- `PUBLISHED` — (none)

#### `src/curation/templates/curation/detail.html` — modify

Update the classification row:

- When `curation.ep_classification` is set: show `ep_classification` with an "EP
  Classification" label; render `ep_evidence_summary` and `ep_additional_notes` in a
  collapsible section below.
- Otherwise: show `curation.suggested_classification` with a "Suggested" label, or
  "------" if `suggested_classification` is `None`.

#### `src/curation/templates/curation/partials/curation/detail_table.html` — modify

This partial renders the classification row inside the detail table. Apply the same
suggested/EP-set conditional as in `detail.html`.

#### `src/curation/templates/curation/list.html` — modify

#### `src/curation/templates/curation/partials/table.html` — modify

The classification column currently renders `curation.classification`. Update both to
render `curation.ep_classification` if set, otherwise
`curation.suggested_classification` (or "------" if `None`). Because
`suggested_classification` is a model property it is available directly in the template
without any view changes.

#### `src/curation/templates/curation/edit/curation.html` — modify

#### `src/curation/templates/curation/forms/curation.html` — modify

Remove the classification field from both the edit template and its reusable form
partial.

#### `src/curation/templates/curation/review.html` — create

New template for the EP review page, accessible only to users with
`has_review_permissions`. Contains:

- A read-only summary section: curation status, score, `suggested_classification`, and
  the full evidence table.
- `EPReviewForm` with the decision radio, classification select, both notes textareas,
  and the panel text input.

### Step 10 — Publication template

#### `src/publication/templates/publication/detail.html` — modify

Line 142 renders `evidence.curation.get_classification_display`. Replace with
`evidence.curation.ep_classification` (using the same `default_if_none` fallback for
curations that have not yet been through EP review).

### Step 11 — Repo changes

#### `src/repo/serializers.py` — modify

`serialize_published_curation` currently serializes `curation.classification`. Replace
with `curation.ep_classification`. A curation can only be published after EP approval,
so `ep_classification` is always set by the time this serializer runs.

#### `src/repo/views.py` — modify

Add two helpers:

- `is_superseded(published_curation)` — returns `True` if any direct or transitive fork
  of `published_curation.curation` has `status == Status.PUBLISHED`. Implemented as a
  recursive traversal of `curation.forks.all()`.
- `get_superseding(published_curation)` — follows the fork chain forward and returns the
  most recently published descendant (`status == Status.PUBLISHED`), or `None` if not
  superseded.

Pass both results as context to the list and detail templates.

#### `src/repo/templates/repo/list.html` — modify

Update the classification column (currently
`published.curation.get_classification_display`) to use `ep_classification`. Mark
superseded entries visually and link forward to the current version.

#### `src/repo/templates/repo/detail.html` — modify

Update the classification display to use `ep_classification`. Add a superseded banner
when `is_superseded` is `True`, with a link to the current version. Show the fork
predecessor link when `curation.forked_from` is set. Add a Fork button (POST to
`curation-fork`) for users with `can_curate`, since forking is initiated from the
published record.

### Step 12 — Admin

#### `src/curation/admin.py` — modify

Remove `classification` from any `list_display`, `readonly_fields`, or `fields`
configuration on `CurationAdmin`. Optionally add `ep_classification` and `ep` to
`list_display` for visibility.

### Step 13 — Fixtures

#### `src/curation/fixtures/test_curations.json` — modify

Remove the `"classification": "LIM"` key. The fixture's `status` is already `"INP"` (In
Progress), so no status update is needed.

### Step 14 — Tests

#### `src/auth_/tests.py` — modify

Add tests for `can_review` on `UserProfile`: verify it is `True` only when both
`has_review_permissions` and `can_curate` are set. Add access-control tests for
`ReviewerViewMixin` asserting that non-EP users receive 403.

#### `src/curation/tests/test_models.py` — modify

- Remove tests for the `classification` field and `validate_classification`.
- Add `suggested_classification` boundary tests: score `0` → `None`; score `1` →
  `LIMITED`; score `24` → `LIMITED`; score `25` → `MODERATE`; score `50` → `MODERATE`;
  score `51` → `STRONG`.
- Add a test that `forked_from` is set correctly and that the fork's evidence count
  matches the source.

#### `src/curation/tests/test_validators.py` — modify

Remove tests for `validate_classification`. Update `validate_status` tests to use
`Status.READY_FOR_REVIEW` instead of `Status.DONE`.

#### `src/curation/tests/test_views.py` — modify

- Add `curation_submit` tests: success path; failure when evidence is not done; failure
  when curation is not `IN_PROGRESS`; access control (non-curator gets 403).
- Add `curation_review` tests: approval path (EP fields set, status → `PROVISIONAL`);
  needs-revision path (EP fields retained, status → `IN_PROGRESS`); access control
  (non-EP user gets 403).
- Add `curation_fork` tests: success path (new curation created, evidence deep-copied,
  `forked_from` set); failure when source is not published.
- Update `curation_publish` tests: change setup from `status=Status.DONE` to
  `status=Status.PROVISIONAL`.
- Update locking tests for `curation_edit_evidence`, `EvidenceCreate`, and
  `EvidenceEdit`: add cases asserting that `READY_FOR_REVIEW` and `PROVISIONAL` statuses
  trigger the lock redirect. (`CurationEdit` was removed in Step 15.)

#### `src/repo/tests.py` — modify

Test setups that simulate published curations use `status=Status.PUBLISHED`. Add tests
for `is_superseded` and `get_superseding`, including a multi-hop fork chain. Add a test
that the Fork button appears on the repo detail page for users with `can_curate`.

### Step 15 — Remove manual status editing

`CurationEditForm` only exposes the `status` field. Because the lifecycle now manages
status transitions automatically (submit → RFR, EP review → PROVISIONAL or back to
IN_PROGRESS, publish → PUBLISHED), curators must not be able to set status manually.

#### `src/curation/forms.py` — modify

Delete `CurationEditForm` entirely.

#### `src/curation/views.py` — modify

Delete the `CurationEdit` class-based view and remove its import of `CurationEditForm`.

#### `src/curation/urls.py` — modify

Remove the `curation-edit` route.

#### `src/curation/templates/curation/partials/buttons.html` — modify

Remove the "Edit Curation" button that linked to `curation-edit`.

#### `src/curation/templates/curation/edit/curation.html` — delete

The template is no longer referenced by any view.

#### `src/curation/tests/test_views.py` — modify

Delete `CurationEditTest`. Update `LockingTest._assert_locked` to no longer hit the
removed `curation-edit` URL — it should test `curation-edit-evidence` only.

#### `src/repo/tests.py` — modify

Delete `ReadOnlyEnforcementTest.test_cannot_edit_published_curation` (the removed URL
made it untestable this way); the remaining `test_cannot_edit_published_evidence` test
is sufficient to verify the locking behaviour for published curations.

### Step 16 — Remove the conflicting evidence field

The `is_conflicting` field on `Evidence` is removed. Evidence is either included or not;
the distinction between conflicting and non-conflicting included evidence is no longer
part of the scoring model.

#### `src/curation/models.py` — modify

Delete the `is_conflicting` field. Simplify the `score` property: instead of subtracting
the score for conflicting included evidence and adding for non-conflicting, simply add
the score for all included evidence.

#### `src/curation/forms.py` — modify

Remove `is_conflicting` from `EvidenceTopLevelEditFormSet.Meta.fields` and `widgets`.

#### `src/curation/models.py` — modify (`Evidence.copy_to`)

Remove `is_conflicting` from the field list in `Evidence.copy_to()`. The inline
deep-copy loop in `curation_fork` no longer exists — copying is handled by the model
method.

#### `src/repo/serializers.py` — modify

Remove `"is_conflicting"` from the evidence serializer output.

#### `src/curation/templates/curation/partials/evidence/detail_table.html` — modify

Remove the "Conflicting" column header and its corresponding cell.

#### `src/curation/templates/curation/forms/evidence.html` — modify

Remove the "Conflicting" column header (the field will no longer appear in the formset
since it is removed from `EvidenceTopLevelEditFormSet.Meta.fields`).

#### `src/curation/fixtures/test_evidence.json` — modify

Remove the `"is_conflicting"` key from the fixture.

#### `src/curation/tests/test_models.py` — modify

Delete `test_conflicting_is_false_when_created`.

#### `src/curation/tests/test_views.py` — modify

Remove `"Conflicting"` from `expected_text` in `CurationDetailTest` and
`CurationEditEvidenceTest`.

#### Migration — add

Generate a migration to remove `is_conflicting` from `Evidence` and
`HistoricalEvidence`.
