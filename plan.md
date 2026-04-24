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

### Step 1 — Add approval permission to `UserProfile`

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

### Step 2 — Extend the workflow status enum

**File:** `src/curation/constants/models/common.py`

- Replace the `Status` class and `STATUS_CHOICES` to contain:
  - `IN_PROGRESS = "INP"` — "In Progress"
  - `PROVISIONAL = "PRV"` — "Provisional"
  - `APPROVED = "APR"` — "Approved"
  - `PUBLISHED = "PUB"` — "Published"
- Remove the `DONE` value.
- Update `Curation.status.help_text` in `src/curation/models.py` to reflect
  the four states.

### Step 3 — Add new fields to `Curation`

**File:** `src/curation/models.py` (`Curation` model, around lines 62-170)

Add:

- `expert_panel_review_notes = TextField(blank=True, default="")`
- `expert_panel_approved_by = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL, related_name="curations_approved")`
- `expert_panel_approved_at = DateTimeField(null=True, blank=True)`
- `classification_override_reason = TextField(blank=True, default="")`

Create migration.

### Step 4 — Add the `CurationStatusEvent` model

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

### Step 5 — Status-transition validators

**File:** `src/curation/validators/models/curation.py`

Update (or replace) `validate_status` so that, when loading an existing
row, the following transitions are the only allowed ones:

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

### Step 6 — Restructure `PublishedCuration`

**File:** `src/repo/models.py`

- Change `curation` from `OneToOneField(unique=True)` to `ForeignKey`.
- Add `snapshot = JSONField()` — populated at publish time via
  `serialize_published_curation` (`src/repo/serializers.py`).
- `version` already exists; compute it at publish time as
  `PublishedCuration.objects.filter(curation=curation).count() + 1`.
- Update `Meta` to include `unique_together = [("curation", "version")]`.

**File:** `src/repo/views.py`

- Update `PublishedCurationDetail` to resolve the latest version by
  default and read display data from `snapshot`, not from the live
  `curation`/`curation.evidence`.
- Update `download_single_json` and `download_all_json` similarly.
- Update `serialize_published_curation` to accept a snapshot dict (so
  downloads render the snapshot, not the live state). We will likely
  store the same serialized shape we already produce today — verify no
  refactor is needed beyond reading from `published.snapshot`.

Create migration.

### Step 7 — Refactor `curation_publish` into discrete transition views

**Files:** `src/curation/views.py`, `src/curation/urls.py`

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

Add matching URL entries in `src/curation/urls.py`:

- `<slug:curation_slug>/submit-for-review` → `curation-submit-for-review`
- `<slug:curation_slug>/approve` → `curation-approve`
- `<slug:curation_slug>/send-back` → `curation-send-back`
- `<slug:curation_slug>/publish` → `curation-publish` (keep the URL name
  so existing reverses don't break; the behavior changes)
- `<slug:curation_slug>/start-new-revision` →
  `curation-start-new-revision`

Add a `can_approve` permission decorator and a
`CanApproveViewMixin` in `src/auth_/permissions.py`, mirroring
`protected_view` and `ProtectedViewMixin`.

### Step 8 — Rework the read-only guards

**File:** `src/curation/views.py`

Replace every `hasattr(object, "publication")` check in
`CurationEdit.dispatch` (~line 68), `curation_edit_evidence` (~line 95),
and `EvidenceEdit.dispatch` (~line 161) with a helper
`can_edit(user, curation)`:

- Nobody can edit a curation when `status == PUBLISHED`. To edit, the
  approver must first click "Start New Revision," which transitions the
  curation to `IN_PROGRESS`.
- Curators can edit when `status == IN_PROGRESS`.
- Approvers can edit when `status in {IN_PROGRESS, PROVISIONAL, APPROVED}`
  (the panel can always edit in non-published states — that enables
  classification override during review).
- The frozen public record for any prior publish lives in
  `PublishedCuration.snapshot` and is never touched by edits to the
  live curation.

### Step 9 — Split the curation edit forms

**File:** `src/curation/forms.py`

- Keep `CurationEditForm` (curators): fields `= ["status"]` (curators
  initiate the submit-for-review transition; they do not edit
  classification directly).
- Add `CurationPanelReviewForm` (approvers): fields
  `= ["classification", "classification_override_reason", "expert_panel_review_notes"]`.

**File:** `src/curation/views.py`

- Route `CurationEdit.get_form_class()` based on
  `request.user.profile.can_approve`.

### Step 10 — Update the detail template

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

### Step 11 — Tests

**Files:** `src/curation/tests/test_views.py`,
`src/curation/tests/test_models.py`, `src/repo/tests.py`

Cover:

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
- Permission gating: a curator cannot approve/publish/start-new-revision;
  an approver without `has_signed_phi_agreement` cannot approve.
- `CurationStatusEvent` is written on every transition with the
  correct `actor`, `from_status`, `to_status`, and note.
- Send-back with an empty note fails and re-renders.
- Publishing sets `status = PUBLISHED`, creates a `PublishedCuration`
  with `version=1`, and both occur atomically (a simulated failure in
  one rolls back the other).
- Re-publishing (start-new-revision → edit → submit → approve → publish)
  creates `version=2` with a refreshed snapshot; the `version=1` row is
  unchanged.
- Start-new-revision transitions `PUBLISHED` → `IN_PROGRESS` and clears
  `expert_panel_approved_by`, `expert_panel_approved_at`, and
  `classification_override_reason`; it does **not** touch any
  `PublishedCuration` rows.
- Edit endpoints are blocked for all users when `status == PUBLISHED`.
- The `PublishedCuration.snapshot` field is populated from the serializer
  and the repo detail view reads from it (not the live curation).
- Editing the live curation after a publish (via start-new-revision)
  does not change the previously-published snapshot.
- Classification can be edited by an approver and cannot be edited by a
  curator (the curator form omits the field).

### Step 12 — Lint, format, type-check, run tests

Run:

```
just py-format
just py-lint
just py-type-check
just test-all
```

Fix any issues before considering Part 1 complete.

---

## Part 2 — History feature (`django-simple-history`)

### Step 13 — Add the dependency

**File:** `pyproject.toml`

- Add `django-simple-history>=3.7` to `[project].dependencies`.
- Sync with whichever package manager this repo uses (`uv`, `pip`, etc.).

### Step 14 — Wire into Django settings

**File:** `src/config/settings/base.py`

- Add `"simple_history"` to `INSTALLED_APPS`.
- Add `"simple_history.middleware.HistoryRequestMiddleware"` to
  `MIDDLEWARE`, after the authentication middleware. This captures
  `request.user` as the history actor automatically.

### Step 15 — Register domain models

Add `history = HistoricalRecords()` to each of:

- `Curation` (`src/curation/models.py`)
- `Evidence` (`src/curation/models.py`)
- `PublishedCuration` (`src/repo/models.py`)
- `CurationStatusEvent` (`src/curation/models.py`) — optional but
  cheap; captures any manual corrections.

Do **not** register lookup models (e.g. `Demographic`).

### Step 16 — Generate and review migrations

Run `just py-manage makemigrations` (or the repo's equivalent).
`django-simple-history` will generate migrations for
`HistoricalCuration`, `HistoricalEvidence`, `HistoricalPublishedCuration`,
and `HistoricalCurationStatusEvent`. Review them to confirm the
tracked field set matches expectations (all concrete fields except FKs
to managers, etc. — the default is usually fine).

### Step 17 — Build the history view

**Files:** `src/curation/views.py`, `src/curation/urls.py`

- Add `CurationHistory` view (class- or function-based — likely function
  so the multi-stream merge is readable).
- URL: `<slug:curation_slug>/history` → name `curation-history`.
- The view assembles a timeline from three streams, merged by timestamp:
  1. `curation.history.all()` — Curation-level edits.
  2. `HistoricalEvidence.objects.filter(curation_id=curation.id)` — all
     Evidence edits for this curation's children.
  3. `CurationStatusEvent.objects.filter(curation=curation)` — workflow
     transitions (also available via the historical table, but the
     first-class events have the review note as a real field).
- Paginate with Django's `Paginator` (page size 25).

### Step 18 — History template

**File:** `src/curation/templates/curation/history.html`

- Timeline layout grouped by day.
- For each entry: actor, timestamp, action type (create/update/delete/
  status change), and — for updates — a diff rendered via
  `new_record.diff_against(old_record)`.
- Write a small template filter or helper that resolves FK fields on a
  historical record to a human label (accessing `record.disease.name`
  works because simple-history stores the FK ID and the live lookup
  still resolves). Handle deleted FK targets defensively.
- Link each entry back to the record it describes (curation detail,
  evidence detail, etc.).

### Step 19 — Expose the history in the curation detail page

**File:** `src/curation/templates/curation/detail.html`

- Add a "History" link near the existing action buttons. Visible to
  anyone who can view the curation.

### Step 20 — Admin integration

**File:** `src/curation/admin.py` (and `src/repo/admin.py` if it exists)

- Swap `admin.ModelAdmin` → `simple_history.admin.SimpleHistoryAdmin`
  for each tracked model. This gives staff an admin-side history
  viewer for free, useful for debugging.

### Step 21 — Tests

**Files:** `src/curation/tests/test_history.py` (new) and existing test
modules as needed.

Cover:

- An edit produces a `HistoricalCuration` row with the expected
  `history_user`, `history_type`, and fields.
- `new.diff_against(old)` returns the expected delta for a specific
  edit.
- The merged timeline orders Curation/Evidence/StatusEvent entries
  correctly by timestamp.
- Pagination works.
- Deleting an Evidence row leaves its history queryable by
  `HistoricalEvidence.objects.filter(curation_id=...)`.

### Step 22 — Lint, format, type-check, run tests

Same suite as Step 12.

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
