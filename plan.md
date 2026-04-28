# Publishing Workflow Redo — Implementation Plan

Right now, when a curation is done, we can publish it directly to the
HLArepo without an expert panel review. This is wrong. We should require
curations to be reviewed by an expert panel before they are published to
the HLArepo.

That's fine, but now we face the issue of tracking the "state" of a
curation. Here are the proposed states:

- (1) in progress
  - either just created or the curator is working on it
- (2) provisional
  - ready for expert panel review
- (3) approved
  - approved by the expert panel, but not yet published to the
    HLArepo
- (4) published
  - publicly viewable in the HLArepo

- **Part 1** — workflow states, permission model, Curation model edits, and
  the refactor of the publish flow.
- **Part 2** — history feature backed by `django-simple-history`.

Part 1 must land before Part 2 (the history feature registers the new models
and events from Part 1).

Each numbered step below is meant to be a single checkpoint commit on the
way to the finished PR: self-contained, builds, migrates, and passes
`just test-all` at HEAD. Tests for new behavior land in the same commit
as the behavior, not in a trailing test-only step. The pre-PR quality
gate (lint/format/type-check/tests across the whole branch) is called
out at the end of each part as a gate, not a commit.

---

## Decisions locked in

- **Workflow states** live on `Curation.status`: `IN_PROGRESS`,
  `PROVISIONAL`, `APPROVED`, `PUBLISHED`. `status` answers "where is the
  live curation right now"; the `PublishedCuration` table answers "what
  versioned public snapshots exist for this curation." Both are needed
  and they answer different questions — re-publishing produces a new
  `PublishedCuration` row while the live `status` returns to
  `PUBLISHED`.
- **Approval permission** is modeled as a stored boolean
  (`has_approval_permissions`) plus a derived property (`can_approve`) on
  `UserProfile`, matching the existing `has_curation_permissions` /
  `can_curate` pattern. `can_approve` is a strict superset of `can_curate`
  (every approver is also a curator).
- **Expert panel approval provenance** on `Curation`:
  `expert_panel_approved_by` (FK User) + `expert_panel_approved_at`
  (DateTime).
- **Classification override**: panel-only edit access to the existing
  `Curation.classification` field, plus a free-form
  `classification_override_reason` TextField on `Curation`.
- **Send-back transitions** require a non-empty note on the
  `CurationStatusEvent` (enforced at the view/form level).
- **Re-publish** is gated by `can_approve`. There is no separate
  "re-publish" permission.
- **Published record immutability**: at publish time we store a JSON
  snapshot on `PublishedCuration` so editing the live `Curation` later does
  not mutate the public record. The repo view reads from the snapshot.
- **`PublishedCuration.curation`** moves from `OneToOneField` to
  `ForeignKey` to allow multiple versions per curation.

---

## Part 1 — Workflow states and Curation model changes

Steps 1–5 are already committed (see git log: `af9deda` through
`72d7ad5`). Their descriptions are preserved below for the PR
description; the remaining work is in Steps 6–9.

### Step 1 — Add approval permission to `UserProfile` *(committed: af9deda)*

**File:** `src/auth_/models.py`

- Add `has_approval_permissions = BooleanField(default=False)` with
  `verbose_name="Approval Permissions"` and appropriate `help_text`.
- Add `can_approve` property:

  ```python
  @property
  def can_approve(self) -> bool:
      return (
          self.user.is_authenticated
          and self.has_signed_phi_agreement
          and self.has_curation_permissions
          and self.has_approval_permissions
      )
  ```

- Create migration.
- Update the admin (`src/auth_/admin.py` if present) so staff can toggle
  the new field.

### Step 2 — Extend the workflow status enum *(committed: 66bac6b)*

**File:** `src/curation/constants/models/common.py`

- Replace the `Status` class and `STATUS_CHOICES` to contain:
  - `IN_PROGRESS = "INP"` — "In Progress"
  - `PROVISIONAL = "PRV"` — "Provisional"
  - `APPROVED = "APR"` — "Approved"
  - `PUBLISHED = "PUB"` — "Published"
- Remove the `DONE` value.
- Update `Curation.status.help_text` in `src/curation/models.py` to reflect
  the four states.
- Update every call site that referenced the old enum (views, validators,
  tests) so the codebase still builds and the existing test suite still
  passes at this commit.

### Step 3 — Add new fields to `Curation` *(committed: 41ab55a)*

**File:** `src/curation/models.py` (`Curation` model, around lines 62-170)

Add:

- `expert_panel_review_notes = TextField(blank=True, default="")`
- `expert_panel_approved_by = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL, related_name="curations_approved")`
- `expert_panel_approved_at = DateTimeField(null=True, blank=True)`
- `classification_override_reason = TextField(blank=True, default="")`

Create migration.

### Step 4 — Add the `CurationStatusEvent` model *(committed: 302bb79)*

**File:** `src/curation/models.py`

Fields:

- `curation = ForeignKey(Curation, on_delete=CASCADE, related_name="status_events")`
- `from_status = CharField(max_length=3, choices=STATUS_CHOICES)`
- `to_status = CharField(max_length=3, choices=STATUS_CHOICES)`
- `actor = ForeignKey(User, null=True, on_delete=SET_NULL, related_name="curation_status_events")`
- `note = TextField(blank=True, default="")`
- `created_at = DateTimeField(auto_now_add=True)`

`Meta`: `db_table = "curation_status_event"`, `ordering = ["-created_at"]`.

Create migration.

### Step 5 — Status-transition validators *(committed: 72d7ad5)*

**File:** `src/curation/validators/models/curation.py`

Update `validate_status` so that, when loading an existing row, the
following transitions are the only allowed ones:

- `IN_PROGRESS` → `PROVISIONAL`
- `PROVISIONAL` → `IN_PROGRESS` (send back)
- `PROVISIONAL` → `APPROVED`
- `APPROVED` → `IN_PROGRESS` (send back after approval — rescinds
  approval and bounces to the curator)
- `APPROVED` → `PUBLISHED`
- `PUBLISHED` → `IN_PROGRESS` (start a new revision)

Forward lifecycle is strictly linear
(`IN_PROGRESS → PROVISIONAL → APPROVED → PUBLISHED`); every backward
edge lands at `IN_PROGRESS`. Skips (e.g. `IN_PROGRESS` → `APPROVED`,
`PROVISIONAL` → `PUBLISHED`, `APPROVED` → `PROVISIONAL`) are
disallowed.

Validation of "the actor has permission for this transition" lives in the
views (Step 7), not in the model-level validator, because permission
depends on `request.user`.

### Step 6 — Edit-guard helper

**Files:** `src/curation/views.py`, `src/curation/tests/test_views.py`

Replace every `hasattr(object, "publication")` check in
`CurationEdit.dispatch` (~line 75), `curation_edit_evidence` (~line 96),
`EvidenceEdit.dispatch` (~line 168), and `curation_publish` (~line 226)
with a helper `can_edit(user, curation)`:

- Nobody can edit a curation when `status == PUBLISHED`. To edit, the
  approver must first click "Start New Revision," which transitions the
  curation to `IN_PROGRESS`.
- Curators can edit when `status == IN_PROGRESS`.
- Approvers can edit when `status in {IN_PROGRESS, PROVISIONAL, APPROVED}`
  (the panel can always edit in non-published states — that enables
  classification override during review).
- The frozen public record for any prior publish lives in
  `PublishedCuration.snapshot` (added in Step 7) and is never touched
  by edits to the live curation.

Tests in this commit:

- Edit endpoints are blocked for all users when `status == PUBLISHED`.
- Curators can edit `IN_PROGRESS`; approvers can edit
  `IN_PROGRESS` / `PROVISIONAL` / `APPROVED`.

This step lands before Step 7 because Step 7 changes the `publication`
reverse descriptor's semantics (`OneToOneField` → `ForeignKey`), which
would silently turn `hasattr(curation, "publication")` into an
always-true check if the call sites still used it.

### Step 7 — Publish-workflow cutover

This is the largest commit in Part 1. The pieces are interlocking and
cannot land separately without leaving the publish flow broken in
between:

- Adding required `snapshot = JSONField()` to `PublishedCuration`
  invalidates the existing `curation_publish` view's
  `PublishedCuration.objects.create(...)` call.
- Replacing `curation_publish` with separate transition views requires
  the new `can_approve` decorator and the new model fields.
- Reading the public record from `snapshot` instead of the live curation
  must happen at the same time `snapshot` becomes required.

So all of it lands in one commit, with tests.

**Files:** `src/repo/models.py`, `src/repo/views.py`,
`src/repo/serializers.py`, `src/curation/views.py`,
`src/curation/urls.py`, `src/auth_/permissions.py`,
`src/curation/tests/test_views.py`, `src/curation/tests/test_models.py`,
`src/repo/tests.py`

Model changes (`src/repo/models.py`):

- Change `curation` from `OneToOneField(unique=True)` to `ForeignKey`.
- Add `snapshot = JSONField()` — populated at publish time via
  `serialize_published_curation` (`src/repo/serializers.py`).
- `version` already exists; compute it at publish time as
  `PublishedCuration.objects.filter(curation=curation).count() + 1`.
- Update `Meta` to include `unique_together = [("curation", "version")]`.

Permission infrastructure (`src/auth_/permissions.py`):

- Add a `can_approve` permission decorator and a `CanApproveViewMixin`,
  mirroring `protected_view` and `ProtectedViewMixin`.

View refactor (`src/curation/views.py`, `src/curation/urls.py`):

Replace the single `curation_publish` view with five view functions,
each creating a `CurationStatusEvent`:

- `curation_submit_for_review` — `IN_PROGRESS` → `PROVISIONAL`
  - Gated by `can_curate`.
- `curation_approve` — `PROVISIONAL` → `APPROVED`
  - Gated by `can_approve`.
  - Sets `expert_panel_approved_by = request.user` and
    `expert_panel_approved_at = timezone.now()`.
- `curation_send_back` — `PROVISIONAL` → `IN_PROGRESS` **or**
  `APPROVED` → `IN_PROGRESS`
  - Gated by `can_approve`.
  - Requires a non-empty `note` from the POST body; if blank, re-render
    with an error.
  - When the source state is `APPROVED`, additionally clear
    `expert_panel_approved_by`, `expert_panel_approved_at`, and
    `classification_override_reason` — the approval no longer stands,
    so its metadata must not linger on the record.
- `curation_publish` — `APPROVED` → `PUBLISHED`, and creates a new
  `PublishedCuration` row with an incremented version and a fresh
  snapshot.
  - Gated by `can_approve`.
  - Wrap the status update and `PublishedCuration` creation in a single
    `transaction.atomic()` block.
- `curation_start_new_revision` — `PUBLISHED` → `IN_PROGRESS`
  - Gated by `can_approve`.
  - Clears `expert_panel_approved_by`, `expert_panel_approved_at`, and
    `classification_override_reason` so the next cycle starts clean.
  - The existing `PublishedCuration` row is **not** touched — the public
    record remains stable.

URL entries in `src/curation/urls.py`:

- `<slug:curation_slug>/submit-for-review` → `curation-submit-for-review`
- `<slug:curation_slug>/approve` → `curation-approve`
- `<slug:curation_slug>/send-back` → `curation-send-back`
- `<slug:curation_slug>/publish` → `curation-publish` (keep the URL name
  so existing reverses don't break; the behavior changes)
- `<slug:curation_slug>/start-new-revision` →
  `curation-start-new-revision`

Repo views (`src/repo/views.py`, `src/repo/serializers.py`):

- Update `PublishedCurationDetail` to resolve the latest version by
  default and read display data from `snapshot`, not from the live
  `curation` / `curation.evidence`.
- Update `download_single_json` and `download_all_json` similarly.
- Update `serialize_published_curation` to accept a snapshot dict (so
  downloads render the snapshot, not the live state). Verify no
  refactor is needed beyond reading from `published.snapshot`.

Migration:

- Generate the schema migration for `PublishedCuration` (FK swap,
  `snapshot` field, `unique_together`).
- If any `PublishedCuration` rows exist in production, include a data
  migration that backfills `snapshot` for those rows by serializing
  the live curation (best-effort frozen state).

Tests in this commit:

- Each valid transition (curator submit, approver approve, approver
  send-back from `PROVISIONAL` → `IN_PROGRESS`, approver send-back from
  `APPROVED` → `IN_PROGRESS`, approver publish, approver
  start-new-revision).
- Send-back from `APPROVED` clears `expert_panel_approved_by`,
  `expert_panel_approved_at`, and `classification_override_reason`.
- Each invalid transition raises `ValidationError` at the model level
  (e.g. `IN_PROGRESS` → `APPROVED`, `PROVISIONAL` → `PUBLISHED`,
  `APPROVED` → `PROVISIONAL`, `PUBLISHED` → anything other than
  `IN_PROGRESS`).
- Permission gating: a curator cannot approve / publish /
  start-new-revision; an approver without `has_signed_phi_agreement`
  cannot approve.
- `CurationStatusEvent` is written on every transition with the correct
  `actor`, `from_status`, `to_status`, and note.
- Send-back with an empty note fails and re-renders.
- Publishing sets `status = PUBLISHED`, creates a `PublishedCuration`
  with `version=1`, and both occur atomically (a simulated failure in
  one rolls back the other).
- Re-publishing (start-new-revision → edit → submit → approve → publish)
  creates `version=2` with a refreshed snapshot; the `version=1` row is
  unchanged.
- Start-new-revision transitions `PUBLISHED` → `IN_PROGRESS` and clears
  the three approval fields; it does **not** touch any
  `PublishedCuration` rows.
- `PublishedCuration.snapshot` is populated from the serializer and the
  repo detail view reads from it (not the live curation).
- Editing the live curation after a publish (via start-new-revision)
  does not change the previously-published snapshot.

### Step 8 — Split the curation edit forms

**Files:** `src/curation/forms.py`, `src/curation/views.py`,
`src/curation/tests/test_views.py`

- Keep `CurationEditForm` (curators): fields `= ["status"]` (curators
  initiate the submit-for-review transition; they do not edit
  classification directly).
- Add `CurationPanelReviewForm` (approvers): fields
  `= ["classification", "classification_override_reason", "expert_panel_review_notes"]`.
- Route `CurationEdit.get_form_class()` based on
  `request.user.profile.can_approve`.

Tests in this commit:

- Classification can be edited by an approver and cannot be edited by a
  curator (the curator form omits the field).
- An approver hitting the edit page receives the panel-review form;
  a curator receives the curator form.

### Step 9 — Update the detail template

**File:** `src/curation/templates/curation/detail.html` (and any included
partials)

- Surface action buttons conditional on `(status, user role)`:
  - `IN_PROGRESS` + curator: "Submit for Review"
  - `PROVISIONAL` + approver: "Approve", "Send Back"
  - `APPROVED` + approver: "Publish", "Send Back"
  - `PUBLISHED` + approver: "Start New Revision"
- When status is `PUBLISHED`, hide the edit buttons (the live record is
  locked; "Start New Revision" is the only way back into editing).
- Show `expert_panel_approved_by` / `_at` when present.
- Show `classification_override_reason` when non-empty.
- Show a list of recent `status_events` (timestamp, actor,
  `from → to`, note).
- When one or more `PublishedCuration` rows exist, link to the latest
  published version in the repo.

UI-only change. Verify by manual smoke test: walk a curation through the
full lifecycle in the browser.

### Pre-PR quality gate for Part 1

Not a commit — a checklist before opening (or merging) the PR:

```
just py-format
just py-lint
just py-type-check
just test-all
```

Fix any issues before considering Part 1 complete.

---

## Part 2 — History feature (`django-simple-history`)

### Step 10 — Add the dependency and wire into Django settings

**Files:** `pyproject.toml`, `src/config/settings/base.py`

- Add `django-simple-history>=3.7` to `[project].dependencies` and sync
  the lockfile with whichever package manager this repo uses (`uv`,
  `pip`, etc.).
- Add `"simple_history"` to `INSTALLED_APPS`.
- Add `"simple_history.middleware.HistoryRequestMiddleware"` to
  `MIDDLEWARE`, after the authentication middleware. This captures
  `request.user` as the history actor automatically.

This commit is behaviorally a no-op until Step 11 registers models.

### Step 11 — Register history on domain models

**Files:** `src/curation/models.py`, `src/repo/models.py`,
`src/curation/admin.py`, `src/repo/admin.py` (if it exists),
`src/curation/tests/test_history.py` (new)

- Add `history = HistoricalRecords()` to:
  - `Curation` (`src/curation/models.py`)
  - `Evidence` (`src/curation/models.py`)
  - `PublishedCuration` (`src/repo/models.py`)
  - `CurationStatusEvent` (`src/curation/models.py`) — optional but
    cheap; captures any manual corrections.
  - Do **not** register lookup models (e.g. `Demographic`).
- Run `just py-manage makemigrations` and review the generated
  migrations for `HistoricalCuration`, `HistoricalEvidence`,
  `HistoricalPublishedCuration`, and `HistoricalCurationStatusEvent`.
  Confirm the tracked field set matches expectations (all concrete
  fields except FKs to managers, etc. — the default is usually fine).
- Swap `admin.ModelAdmin` → `simple_history.admin.SimpleHistoryAdmin`
  for each tracked model, giving staff an admin-side history viewer
  for free, useful for debugging.

Tests in this commit:

- An edit produces a `HistoricalCuration` row with the expected
  `history_user`, `history_type`, and tracked fields.
- Deleting an Evidence row leaves its history queryable by
  `HistoricalEvidence.objects.filter(curation_id=...)`.

### Step 12 — Build the history view, template, and detail link

**Files:** `src/curation/views.py`, `src/curation/urls.py`,
`src/curation/templates/curation/history.html`,
`src/curation/templates/curation/detail.html`,
`src/curation/tests/test_history.py`

View (`src/curation/views.py`, `src/curation/urls.py`):

- Add `CurationHistory` view (likely function-based so the multi-stream
  merge is readable).
- URL: `<slug:curation_slug>/history` → name `curation-history`.
- The view assembles a timeline from three streams, merged by
  timestamp:
  1. `curation.history.all()` — Curation-level edits.
  2. `HistoricalEvidence.objects.filter(curation_id=curation.id)` — all
     Evidence edits for this curation's children.
  3. `CurationStatusEvent.objects.filter(curation=curation)` — workflow
     transitions (also available via the historical table, but the
     first-class events have the review note as a real field).
- Paginate with Django's `Paginator` (page size 25).

Template (`src/curation/templates/curation/history.html`):

- Timeline layout grouped by day.
- For each entry: actor, timestamp, action type (create / update /
  delete / status change), and — for updates — a diff rendered via
  `new_record.diff_against(old_record)`.
- A small template filter or helper resolves FK fields on a historical
  record to a human label (accessing `record.disease.name` works
  because simple-history stores the FK ID and the live lookup still
  resolves). Handle deleted FK targets defensively.
- Link each entry back to the record it describes (curation detail,
  evidence detail, etc.).

Detail page (`src/curation/templates/curation/detail.html`):

- Add a "History" link near the existing action buttons, visible to
  anyone who can view the curation.

Tests in this commit:

- `new.diff_against(old)` returns the expected delta for a specific
  edit.
- The merged timeline orders Curation / Evidence / StatusEvent entries
  correctly by timestamp.
- Pagination works.

### Pre-PR quality gate for Part 2

Same checklist as Part 1.

---

## Open questions (none blocking)

No open questions at plan time. All four items from the design
discussion (`058__Redo-Publishing-Workflow.md`) have been resolved:

1. Expert panel approval provenance — DateTime + FK User on Curation.
2. Classification override reason — free-form text on Curation.
3. Send-back note — required, enforced in view.
4. Approval permission — stored boolean plus derived property on
   `UserProfile`.

---

## Out of scope

- Forking off an arbitrary snapshot to start a new curation. The
  re-publish workflow (edit the live curation, get re-approval, publish
  v2) covers the realistic use cases; true fork/branch semantics can be
  added later as a "clone curation" action if needed.
- Deriving `Curation.classification` from `Curation.score`. The
  `classification` field remains manually set; the panel's override
  ability is just edit access plus the `classification_override_reason`
  field.
- Moving to `django-auditlog` in addition to `django-simple-history`.
  The history feature needs full row snapshots for rendering, so
  simple-history is the single tool for this use case.
