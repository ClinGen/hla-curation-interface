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

## Follow-Up: Expert Panel Feedback

This section was added after the plan above was implemented (commit `6bc9d88`, with the
"fork" to "copy" rename in `cec04de`). The sections above describe the lifecycle using
the status names that shipped (Ready for Review, Provisional). This follow-up renames
them; where the two disagree, this section is current.

### The Problem

The expert panel has used the review workflow and sent back feedback, and three open
GitHub issues (#58, #62, #85) that the original plan mostly covered still have loose
ends. What is left:

- **Status names don't match how the panel talks.** For the panel, "provisional" means
  "finished by the curator and waiting for us," not "approved by us." Today's
  Ready for Review status should be called **Provisional**, and today's Provisional
  status should be called **Approved**. This is more than a label change. The stored
  code `PRO` means Provisional today, so if we reused `PRO` for the new meaning, one
  code would mean two different things depending on when a row was written.
- **The review date is wrong.** The only dates we have are `added_at` and `updated_at`,
  plus the history row written when the status changed. All of these record when
  someone clicked a button in the HCI. The panel wants to record the date the panel
  actually met and reviewed the curation, which can be days or weeks earlier.
- **An override isn't recorded as an override.** The reviewer picks `ep_classification`
  from a dropdown. If it differs from `suggested_classification`, a JavaScript
  `confirm()` pops up, but nothing about the override is saved. #62 asks that an
  override require a note, and the panel wants that note kept in its own field, apart
  from the general notes.
- **EP notes are hard to find on the curation detail page.** `curation/detail.html`
  shows the EP notes only when `ep_classification` is set. It labels
  `ep_evidence_summary` as "Classification Notes." It doesn't show the panel or the
  classification that the notes belong to. When a reviewer sends a curation back
  without choosing a classification, which is the normal case, the curator can't see
  the panel's feedback at all. The original plan kept these fields so the curator
  *could* see them.
- **The public repository shows too little.** `repo/detail.html` reuses the internal
  `detail_table.html` and evidence table. It never shows the evidence summary (#85),
  and it doesn't link out to Mondo or the ClinGen Allele Registry (CAR), even though
  `Disease.iri` and `Allele.car_id` are stored and the allele and disease detail pages
  already link to them.
- **Curators can't tell what will become public.** Some fields end up in HLArepo and
  the JSON export (the evidence summary, the classification, most evidence data).
  Others stay internal (every `*_notes` field on `Evidence`). Nothing on the forms tells
  a curator or reviewer which is which.
- **A score of 0 shows as `------`.** #62 asks for "No classification set" instead.
- **Confirmations use `window.confirm`.** #58 asks for a Bulma modal instead. There are
  four `confirm()` calls: Submit for Review and Publish in
  `curation/partials/buttons.html`, Copy and Recurate in `repo/detail.html`, and the
  override warning in `curation/review.html`. Publish is also a plain `<a href>` link,
  so a `GET` request publishes the curation. Any link prefetcher or crawler that
  follows the link could publish it.

The goal is to close all of these so the workflow matches the panel's vocabulary and
records what the panel decided, when it decided, and why. The public record should show
the parts that matter.

**Split with `docs/plans/007-public-repo-site.md`.** That plan (GitHub #87) makes
HLArepo reachable without logging in, possibly on its own hostname. It owns access
control, routing, and hosting for the repo pages. This follow-up owns what those pages
show: the evidence summary, EP fields, review date, and Mondo/CAR links. Both plans edit
`repo/templates/repo/detail.html`, so whichever lands second should rebase onto the
other. This section doesn't change who can see the page. The internal links that the
reused partials render on the repo page (the "View History" button pointing at
`curation-history`, and the evidence rows linking to `evidence-detail`) are left to
007.

### The Technical Plan

**Status rename with new codes.** We rename the codes, not just the labels, and we use
two codes that have never been stored: Ready for Review `RFR` becomes Provisional `PRV`,
and Provisional `PRO` becomes Approved `APR`. Because neither `PRV` nor `APR` has ever
been written, the data migration doesn't depend on order. No row passes through an
ambiguous state, and `PRO` stops meaning anything. If we reused `PRO` for the new
Provisional, the migration would have to run `PRO → APR` strictly before `RFR → PRO`,
and any code or export that saw a `PRO` would have to know which era it came from. In
Python, `Status.READY_FOR_REVIEW` becomes `Status.PROVISIONAL` and the old
`Status.PROVISIONAL` becomes `Status.APPROVED`. That Python rename also has an order
hazard, covered in Step 1. The same migration updates `HistoricalCuration` rows so the
history views keep resolving status labels.

A local-state wrinkle: the local `src/hci.db` already has
`curation.0021_rename_status_codes` recorded as applied (on 2026-09-11), and
`C000005` is stored as `APR`. The migration file is no longer in the tree; only a stale
`.pyc` remains in `src/curation/migrations/__pycache__/`. The `.pyc` shows it used this
same mapping, `{"RFR": "PRV", "PRO": "APR"}`, on `Curation` and `HistoricalCuration`,
followed by an `AlterField` on `Curation.status` and one on `Evidence.num_fields`. The
local `curation_historicalcuration` table still holds `RFR` and `PRO` rows, so the
history part didn't take effect locally. `makemigrations --check` also reports pending
`num_fields` label changes left over from `f85bc1d`. Step 1 recreates the migration
under the same name so it lines up with the local database (see Open Question 1).
`docs/tickets/012-max-length-constants.md` also plans a migration for the `num_fields`
drift. If the name doesn't need to be kept, that ticket's migration takes `0021` and
this one becomes `0022_rename_status_codes`.

**EP review date.** Add a `DateField`, `ep_review_date`, set by the reviewer on the
review form. It's required when approving, optional when sending back, and can't be in
the future. It's shown internally and publicly and included in the JSON export. The
date the HCI recorded the approval is still available from history, as the original plan
chose.

**Classification override.** `ep_classification` stays the single authoritative
classification. Add `ep_override_reason` (a `TextField`). On the review form,
`ep_classification` starts out set to the suggested classification. If the reviewer
picks anything else, `EPReviewForm.clean()` requires `ep_override_reason`. "Anything
else" includes every choice when the suggestion is `None` (score 0), and `DEFINITIVE`,
which is never suggested. The textarea is shown only when the selection differs from the
suggestion, so the JavaScript `confirm()` goes away. Add a model property,
`Curation.is_classification_overridden`, so templates and serializers don't repeat the
comparison.

**Classification display.** Add one template partial,
`curation/partials/classification.html`, that renders the EP classification, the
suggested classification, or "No Classification Set." `detail_table.html`,
`CurationTable.render_classification`, and
`PublishedCurationTable.render_classification` all route through the same logic. Today
each of them has its own copy of the `if` chain.

**EP feedback panel.** Replace the ad hoc notification in `curation/detail.html` with a
partial, `curation/partials/ep_review.html`. It shows every non-empty EP field: panel,
review date, classification, override reason, evidence summary, and additional notes.
It appears whenever *any* EP field is set, and it uses a warning style with a "Sent back
for revision" heading when the status is In Progress. The review page includes the same
partial, so a reviewer sees earlier feedback when a curation comes back.

**Public repo content.** Add a repo-specific summary partial,
`repo/partials/summary.html`, that shows only public information. It covers the entity
(with a CAR link for alleles, and for each allele in a haplotype), the disease (with a
Mondo link through `Disease.iri`), the classification, the panel, the review date, the
publication date, and the evidence summary as its own block. `repo/detail.html` uses it
in place of `curation/partials/curation/detail_table.html`. The serializer gets the new
fields and the disease IRI.

**Public-field indicator.** Add a single source of truth, `repo/constants.py`, with
`PUBLIC_CURATION_FIELDS` and `PUBLIC_EVIDENCE_FIELDS`. The serializers use these lists,
and a test checks that the lists match what the serializers emit. A small template
partial, `common/public_badge.html`, renders a globe icon with a tooltip ("Shown
publicly in HLArepo"). The form field partials show the badge when they receive
`public=True`. The review form and evidence edit form pass that flag for fields in the
lists.

**Confirmation modal.** Add one Bulma modal partial, `common/confirm_modal.html`, and a
small script, `static/hci/js/confirm-modal.js`. The script intercepts form submission on
any `<form data-confirm="...">` and shows the modal. It submits the form only after the
user confirms. Publish becomes a `POST` form, and `curation_publish` rejects other
methods.

### Alternatives

#### Relabel only and keep codes `RFR`/`PRO`

Changing only `CURATION_STATUS_CHOICES` labels would avoid a data migration. We rejected
it because `PRO` would then mean "Approved" while the Python constant, the code, and
every old export say "Provisional." New readers would be confused for as long as the
code exists.

#### Reuse `PRO` for the new Provisional

This keeps the three-letter mnemonic tidy (`PRO` = Provisional), but the migration then
depends on order. Worse, historical rows and previously downloaded JSON would silently
change meaning. New codes cost nothing and remove the hazard.

#### A separate `ep_override_classification` field

The notes suggest a "separate field for when you need to override the suggested
classification." One reading is a second classification column that is null unless the
panel overrides. That leaves two classification fields that every reader must reconcile
(`override or ep_classification`). We keep one authoritative `ep_classification` and put
the separate field on the *reason*. That reason is the information the panel actually
asked to capture. `is_classification_overridden` gives templates the flag they need.

#### `title` attribute versus a CSS tooltip

Bulma ships no tooltip component. A plain `title` attribute works everywhere and needs
no CSS, but it doesn't appear on touch devices or keyboard focus. We use a `title` plus
visually hidden text (`is-sr-only`) for screen readers. We can switch to a CSS tooltip
in `custom.css` later if the panel finds `title` too subtle.

### Open Questions

1. **Local database and the `0021_rename_status_codes` record.** The local `hci.db`
   already records `curation.0021_rename_status_codes` as applied, with `PRV`/`APR`
   codes. Step 1 recreates a migration under that exact name with the same mapping, so
   the local DB and new environments agree. Because Django won't re-run it locally, the
   local history rows still holding `RFR`/`PRO` will need a one-off fix, or the local DB
   can be restored from a backup and migrated from scratch. Was the old migration ever
   applied to staging or production? If it was, Step 1 must match it exactly. If it
   wasn't, the name only matters locally. *Blocks Step 1.*
2. **Which EP fields are public?** Today the JSON export includes `ep_additional_notes`
   and the internal `ep` ID, and the repo page shows neither. Should
   `ep_additional_notes` and `ep_override_reason` appear in HLArepo and the JSON, or
   stay internal? This plan assumes the evidence summary, classification, panel, and
   review date are public, and the other two are internal. It also assumes
   `needs_review` and the evidence `*_notes` fields stay internal. *Blocks Step 7, and
   the public/private split in Step 3.* **Partly answered:** `ep_additional_notes` is
   public. The repo page shows it under an "Additional Notes" heading, and the JSON
   export keeps it. `ep_override_reason` is still open.
3. **Does "standardized" in #85 mean templated text?** The issue title is "Standardized
   Evidence Summary Text." This plan treats that as free text entered by the reviewer.
   If the panel wants a generated starting template (for example, "HLA-X has a {class}
   association with {disease} based on N studies..."), that's a follow-up that
   pre-fills `ep_evidence_summary` on the review form. *Does not block this plan.*
4. **Should the repo page credit the reviewer?** The HCI user who recorded the review
   isn't stored as a field. Only history has it. This plan doesn't show it. *Does not
   block.*

### Detailed Implementation

#### Step 1 — Rename statuses to Provisional and Approved

Do the Python rename in two passes in this order. First rename `Status.PROVISIONAL` to
`Status.APPROVED` everywhere. Then rename `Status.READY_FOR_REVIEW` to
`Status.PROVISIONAL`. The reverse order merges the two constants. Template string
literals get the same two passes: `"PRO"` → `"APR"` first, then `"RFR"` → `"PRV"`.

##### `src/curation/constants/models/common.py` — modify

`Status` becomes `IN_PROGRESS = "INP"`, `DONE = "DNE"`, `PROVISIONAL = "PRV"`,
`APPROVED = "APR"`, `PUBLISHED = "PUB"`. `CURATION_STATUS_CHOICES` labels become "In
Progress," "Provisional," "Approved," and "Published." Update
`CURATION_STATUS_TRANSITIONS` to match: `INP → {PRV}`, `PRV → {INP, APR}`,
`APR → {PUB}`.

##### Python status references — modify

- `src/curation/models.py`
- `src/curation/views.py`
- `src/curation/validators/models/curation.py`

Apply the two-pass rename. `is_locked`, `curation_submit`, `curation_review`,
`validate_status`, and the `can_submit` message ("submitted for review") keep their
behavior. Update the docstrings that say "provisional" in the old sense, such as
`curation_publish` ("Publishes an approved curation").

##### `src/curation/tables.py` — modify

`render_status`: the `PROVISIONAL` branch renders "Provisional." It currently renders
"Needs Review" for `RFR`, which doesn't match the detail page either. The `APPROVED`
branch renders "Approved."

##### Status templates — modify

- `src/curation/templates/curation/detail.html`
- `src/curation/templates/curation/partials/buttons.html`
- `src/curation/templates/curation/partials/curation/detail_table.html`

Apply the two-pass literal rename and update the `{# ... #}` comments and tag text. The
banner for `PRV` reads "This curation is provisional and awaiting expert panel review."
The banner for `APR` reads "This curation has been approved by the expert panel and is
ready to publish."

##### `src/curation/migrations/0021_rename_status_codes.py` — create

Generate it with `makemigrations curation --name rename_status_codes` after the
constants change. That produces the `AlterField` for `Curation.status` and picks up the
pending `Evidence.num_fields` and `HistoricalEvidence.num_fields` changes. Then add a
`RunPython` operation *before* the `AlterField`s. It maps `{"RFR": "PRV", "PRO": "APR"}`
on both `Curation` and `HistoricalCuration` through `apps.get_model`, and its reverse
function applies the inverse mapping. The operation can run in any order because the
target codes are new. See Open Question 1 about the name.

##### Tests — modify

- `src/curation/tests/test_views.py`
- `src/curation/tests/test_models.py`
- `src/repo/tests.py`

Apply the rename. Write these tests first: a migration test that uses
`MigrationExecutor` to migrate to `0020`, create rows with `RFR`/`PRO` (including
historical rows), migrate forward, and assert `PRV`/`APR`; and the reverse. Add
`CurationTable.render_status` tests for the new labels. Add a transitions test asserting
that `APR → PRV` is illegal.

##### `src/curation/README.md` — modify

Update the `constants/models/common.py`, `detail.html`, and `buttons.html` entries to
use the new status names.

#### Step 2 — EP review date

##### `src/curation/models.py` — modify

Add `ep_review_date = models.DateField(null=True, blank=True, verbose_name="EP Review
Date", help_text="The date the expert panel reviewed the curation.")`.

##### `src/curation/forms.py` — modify

Add `ep_review_date` to `EPReviewForm` as a `DateField` with
`DateInput(attrs={"type": "date", "class": "input"})`, `required=False`. In `clean()`,
require it when `decision == "approved"`, and reject dates later than
`timezone.localdate()` in both branches.

##### `src/curation/views.py` — modify

`curation_review` saves the field and pre-populates it on GET.

##### `src/curation/templates/curation/review.html` — modify

Render the field with `common/form/input/text.html` and `type="date"`.

##### `src/repo/serializers.py` — modify

Add `"ep_review_date"` (ISO date or `None`) under `"curation"`.

##### `src/curation/admin.py` — modify

Add `ep_review_date` to the `Curation` admin's `list_display`.

##### Migration — add

Generate with `makemigrations`.

##### Tests — modify

In `src/curation/tests/test_views.py`, add to `CurationReviewTest`: approving without a
date fails; approving with a future date fails; approving with today's date saves it;
needs-revision without a date succeeds. In `src/repo/tests.py`, add to
`JSONDownloadViewTest`: the export includes `ep_review_date`.

Update the `forms.py`, `models.py`, and `review.html` entries in
`src/curation/README.md`.

#### Step 3 — Classification override reason

##### `src/curation/models.py` — modify

Add `ep_override_reason = models.TextField(null=True, blank=True, verbose_name="EP
Override Reason", help_text="Why the panel chose a classification other than the
suggested one.")`. Add a property, `is_classification_overridden`, that returns `True`
when `ep_classification` is set and differs from `suggested_classification`.

##### `src/curation/forms.py` — modify

`EPReviewForm.__init__` takes a `suggested_classification` keyword argument and stores
it. Add `ep_override_reason` (a `Textarea`, `required=False`). In `clean()`, when
approving and `ep_classification != self.suggested_classification`, require
`ep_override_reason`. When approving without an override, clear
`ep_override_reason` so a stale reason from an earlier review isn't kept.

##### `src/curation/views.py` — modify

`curation_review` passes `suggested_classification=curation.suggested_classification`
to the form. On GET, it sets `initial["ep_classification"]` to
`curation.ep_classification or curation.suggested_classification`, and it saves
`ep_override_reason`.

##### `src/curation/templates/curation/review.html` — modify

Remove the `confirm()` script. Render `ep_override_reason` in a wrapper that is hidden
unless the selected classification differs from the suggestion. A few lines of inline
JavaScript toggle `is-hidden` on `change`. The server-side `clean()` is the real guard.
Label the classification select "Classification (suggested: X)."

##### `src/repo/serializers.py` — modify

Include `ep_override_reason` only if Open Question 2 says it is public. Otherwise leave
it out.

##### Migration — add

Generate with `makemigrations`.

##### Tests — modify

In `src/curation/tests/test_models.py`, test `is_classification_overridden` in these
cases: no EP classification; matching; differing; `DEFINITIVE`; a score of 0 with any
classification. In `src/curation/tests/test_views.py`, add to `CurationReviewTest`:
approving with the suggested classification needs no reason; approving with an
override and no reason fails with a field error; approving with an override and a
reason saves both; approving without an override clears an old reason.

Update the `models.py`, `forms.py`, and `review.html` entries in
`src/curation/README.md`.

#### Step 4 — Shared classification display and "No Classification Set"

##### `src/curation/models.py` — modify

Add a `classification_display` property. It returns
`get_ep_classification_display()` if `ep_classification` is set, otherwise the
`CLASSIFICATION_CHOICES` label of `suggested_classification`, otherwise
`"No Classification Set"`. Add an `is_classification_suggested` property that is `True`
when no EP classification is set.

##### `src/curation/templates/curation/partials/classification.html` — create

Renders `<span class="tag">{{ object.classification_display }}</span>`. When
`is_classification_suggested` is true, it adds a light "Suggested" tag next to it.

##### `src/curation/templates/curation/partials/curation/detail_table.html` — modify

Replace the hand-written `if sc == "DEF"` chain with the partial. The row label is
always "Classification."

##### Table classes — modify

- `src/curation/tables.py`
- `src/repo/tables.py`

Have `render_classification` return `record.classification_display` (or
`record.curation.classification_display`). This removes the duplicated fallback logic.

##### Tests — modify

In `src/curation/tests/test_models.py`, test `classification_display` for a score of 0,
a positive score, and an EP-set classification. In `src/curation/tests/test_views.py`,
test that `CurationDetailTest` and `CurationListTest` show "No Classification Set" for
an empty curation. In `src/repo/tests.py`, add the same check to `RepoSearchViewTest`.

Add `partials/classification.html` to `src/curation/README.md` and update the
`tables.py` entries in `src/curation/README.md` and `src/repo/README.md`.

#### Step 5 — EP feedback on the curation detail page

##### `src/curation/models.py` — modify

Add a `has_ep_feedback` property that is `True` if any of `ep_classification`,
`ep_evidence_summary`, `ep_additional_notes`, `ep_override_reason`, or
`ep_review_date` is set.

##### `src/curation/templates/curation/partials/ep_review.html` — create

A Bulma `message` block. Use `is-warning` with the heading "Sent Back for Revision"
when the status is In Progress, otherwise `is-info` with "Expert Panel Review." Show
labeled rows for the panel (the display name from `EP_CHOICES`), review date,
classification, override reason, evidence summary, and additional notes. Skip empty
rows. Render text with `linebreaks`.

##### `src/curation/templates/curation/detail.html` — modify

Replace the current `{% if object.ep_classification %}` notification with
`{% if object.has_ep_feedback %}{% include "curation/partials/ep_review.html" %}`.

##### `src/curation/templates/curation/review.html` — modify

Include the same partial above the form when `object.has_ep_feedback`, so a re-review
shows the previous feedback.

##### Tests — modify

In `src/curation/tests/test_views.py`, add to `CurationDetailTest`: after a
needs-revision review with only additional notes and no classification, the notes and
the "Sent Back for Revision" heading appear. After approval, the evidence summary
appears under "Evidence Summary," not "Classification Notes." Add a
`has_ep_feedback` model test.

Add `partials/ep_review.html` to `src/curation/README.md` and update the `detail.html`
entry.

#### Step 6 — Public repo content: evidence summary and linkouts

##### `src/repo/templates/repo/partials/summary.html` — create

A table showing: HCI Curation ID; allele (with CAR linkout via `common/linkout.html` to
`https://reg.clinicalgenome.org/allele/ui/hla/id/<car_id>`) or haplotype (with each
member allele and its CAR linkout); disease (with Mondo linkout via `Disease.iri`,
falling back to plain `mondo_id` text); classification (from the Step 4 partial);
expert panel; EP review date; and published date (`published.published_at`). Below the
table, render an "Evidence Summary" heading with the evidence summary in a `<p>`, then
a smaller "Additional Notes" heading with `ep_additional_notes` in a `<p>`.

##### `src/repo/templates/repo/detail.html` — modify

Replace the `curation/partials/curation/detail_table.html` include with
`repo/partials/summary.html`. Keep the superseded and copied-from notices, the buttons,
and the evidence table. The evidence table stays as-is here; 007 decides whether its
links change.

##### `src/repo/views.py` — modify

In `PublishedCurationDetail.get_object`, add
`select_related("curation__allele", "curation__haplotype", "curation__disease")` and
`prefetch_related("curation__haplotype__alleles")` so the linkouts don't add queries.

##### `src/repo/serializers.py` — modify

Add `"iri"` to the disease dict and `"car_id"` to each haplotype allele.

##### Tests — modify

In `src/repo/tests.py`, add to `PublishedCurationDetailViewTest`: the evidence summary
text appears; the CAR link appears for an allele curation; the Mondo IRI link appears;
each haplotype allele's CAR link appears; `ep_additional_notes` appears. In `JSONDownloadViewTest`, check for the disease `iri` and the
haplotype allele `car_id`.

Add `templates/repo/partials/summary.html` to `src/repo/README.md` and update the
`detail.html` and `serializers.py` entries.

#### Step 7 — Mark public fields on forms

##### `src/repo/constants.py` — create

Define `PUBLIC_CURATION_FIELDS` and `PUBLIC_EVIDENCE_FIELDS` as `frozenset`s of model
field names, following the Open Question 2 decision.

##### `src/repo/serializers.py` — modify

Build the EP part of the `"curation"` dict from `PUBLIC_CURATION_FIELDS`, so a field
can't be public in one place and private in another.

##### `src/common/templates/common/public_badge.html` — create

`<span class="icon has-text-info" title="Shown publicly in HLArepo">` with
`bi-globe2` and an `is-sr-only` text label.

##### Form field partials — modify

- `src/common/templates/common/form/textarea.html`
- `src/common/templates/common/form/input/text.html`
- `src/common/templates/common/form/input/radio.html`
- `src/common/templates/common/form/select/default.html`

Next to the label, `{% if public %}{% include "common/public_badge.html" %}{% endif %}`.

##### `src/common/templatetags/custom_filters.py` — modify

Add an `is_public` filter, `{{ form.field.name|is_public:"evidence" }}`, that checks the
constants, so templates don't hard-code the lists. Add filter tests to
`src/common/tests.py`.

##### Form templates — modify

- `src/curation/templates/curation/review.html`
- `src/curation/templates/evidence/edit.html`

Pass `public=...` to each field include using the filter.

##### Tests — modify

In `src/repo/tests.py`, test that the serializer's curation keys and evidence keys are
exactly the constants plus the structural keys (IDs, entity, disease). In
`src/curation/tests/test_views.py`, test that the review page renders the badge next to
Evidence Summary and not next to Additional Notes, and that the evidence edit page
renders it next to P-Value and not next to `p_value_notes`.

Update `src/repo/README.md` (for `constants.py`) and `src/common/README.md` (for
`public_badge.html`, the field partials, and the filter).

#### Step 8 — Bulma confirmation modal and POST-only publish

##### `src/common/templates/common/confirm_modal.html` — create

A single Bulma `modal` with `modal-background`, a `modal-card` holding a message
`<p id="confirm-modal-message">`, and Cancel and Confirm buttons. Include it once in
`src/templates/layouts/base.html`.

##### `src/static/hci/js/confirm-modal.js` — create

On `submit` of any `form[data-confirm]`, prevent the default action, put the message in
the modal, and open it by adding `is-active`. Confirm calls `form.submit()`. Cancel,
the background, and Escape close the modal. Load it from `base.html`. It's hand-written,
so it doesn't go through `build.js`.

##### `src/curation/templates/curation/partials/buttons.html` — modify

Replace the `onclick="return confirm(...)"` handlers with `data-confirm="..."` on the
form. Turn the Publish `<a>` into a `<form method="post">` with `{% csrf_token %}`.

##### `src/repo/templates/repo/detail.html` — modify

Do the same for the Copy and Recurate form.

##### `src/curation/views.py` — modify

In `curation_publish`, redirect to `curation-detail` without publishing if
`request.method != "POST"`. This matches `curation_submit` and `curation_copy`.

##### Tests — modify

In `src/repo/tests.py`, update `CurationPublishViewTest` to `POST`, and add a test that
a `GET` doesn't publish. In `src/curation/tests/test_views.py`, add a template test
that no `confirm(` remains in the rendered detail and review pages and that
`data-confirm` is present.

Add the modal partial to `src/common/README.md`, the script to `src/static/README.md`,
and the base template change to `src/templates/README.md`.

### Sources

- Notes: "HCI: Work on EP review feedback"
  - "Change fork button to 'copy and recurate'" (already done in `cec04de`)
  - "Should display EP notes in details page if they exist"
  - "Show evidence summary, other important info in the repo (MONDO links, CAR links,
    etc.)"
  - "Need EP review date (not the date it was actually approved in our system)"
  - "Visually show which fields will be public? Icon with tooltip?"
  - "Separate field for when you need to override the suggested classification"
  - "Change name of provisional to approved"
  - "Change name of ready for review to provisional"
- https://github.com/ClinGen/hla-curation-interface/issues/58
- https://github.com/ClinGen/hla-curation-interface/issues/62
- https://github.com/ClinGen/hla-curation-interface/issues/85
- Related: https://github.com/ClinGen/hla-curation-interface/issues/87
  (`docs/plans/007-public-repo-site.md`)
