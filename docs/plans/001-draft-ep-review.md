# Expert Panel Review

## Overview

Right now, any curator with `can_curate` permissions can publish any curation whose
status is `Done` with a single click. There is no review step and no gate between a
curator finishing their work and that work appearing in the public HLA repository.

This plan introduces a mandatory expert panel (EP) review stage that sits between a
curator marking a curation ready and that curation being published. It also replaces the
current curator-chosen classification with a score-derived suggestion, with the EP
setting the authoritative classification at review time.

______________________________________________________________________

## Prerequisites

This plan assumes that `django-simple-history` has already been integrated across the
codebase in a prior, dedicated PR. The EP review workflow involves overwriting fields
when a curation is sent back for revision, and the audit trail of previous review rounds
lives in the history tables rather than on the model itself. If history is not in place
first, that audit trail is simply lost.

______________________________________________________________________

## The New Status State Machine

The existing two-state model (`In Progress` → `Done` → published) is replaced with a
four-state model. `Done` is removed entirely.

```
  +-------------+       submit for review       +------------------+
  | In Progress | --------------------------->  | Ready for Review |
  +-------------+                               +------------------+
        ^                                               |
        |                                    EP reviews |
        |  needs revision                               |
        | <-------------------------------------------- |
                 (ep fields cleared on revert)          |  approved
                                                        v
                                                 +-------------+
                                                 | Provisional |
                                                 +-------------+
                                                        |
                                                        |  publish
                                                        v
                                                 +-----------+
                                                 | Published |
                                                 +-----------+
```

The transitions are:

- **In Progress → Ready for Review**: the curator clicks "Submit for Review." All
  included evidence must have status `Done` before this transition is allowed, matching
  the constraint that `validate_status` currently enforces on the old `Done` status.

- **Ready for Review → Provisional**: an EP reviewer approves the curation, setting the
  EP fields and locking the curation.

- **Ready for Review → In Progress**: an EP reviewer sends the curation back for
  revision. The EP fields are cleared and the curation becomes editable again. The
  previous round's EP data is preserved in the django-simple-history audit log.

- **Provisional → Published**: any curator with `can_curate` publishes the curation to
  the HLA repository, creating a `PublishedCuration` record as today.

______________________________________________________________________

## Locking

The edit views (`CurationEdit`, `curation_edit_evidence`, `EvidenceEdit`) currently
block edits once a `PublishedCuration` record exists. This logic needs to extend to
cover `Ready for Review` and `Provisional` as well. A curation in either of those states
is locked for editing. The lock lifts only if the curation is sent back to
`In Progress`.

______________________________________________________________________

## Permissions

The existing `UserProfile` model has `has_curation_permissions`. A new flag,
`has_ep_review_permissions`, is added alongside it. Any user with this flag set can
access the EP review view and act on behalf of the expert panel. The existing
`can_curate` property, which currently gates all curation views, is unchanged — EP
reviewers are a subset of users who also have `can_curate`.

The `ProtectedViewMixin` and `protected_view` decorator in `auth_/permissions.py` remain
as-is. A new mixin or decorator, `EPReviewViewMixin` / `ep_review_view`, is added that
additionally checks `has_ep_review_permissions`.

______________________________________________________________________

## Classification

### Removing the Curator-Chosen Field

The `classification` field is currently a `CharField` on the `Curation` model that the
curator sets manually, constrained by the `validate_classification` validator. Both the
field and that validator are removed. Classification is no longer something a curator
sets directly.

### `suggested_classification` as a Property

A `suggested_classification` property is added to the `Curation` model. It derives a
classification purely from the current score:

```
score == 0          →  NOT_SET
0 < score < 25      →  LIMITED
25 <= score <= 50   →  MODERATE
score > 50          →  STRONG
```

This is a computed value, not a stored field. It changes as evidence is added or edited.
Because editing is locked once a curation enters `Ready for Review`, the suggested
classification cannot drift during the review window.

The `Classification` enum in `curation/constants/models/curation.py` gains a `NOT_SET`
value. `DEFINITIVE` remains in the enum — it is not reachable via the suggestion logic,
but is available for EP override.

### `ep_classification` as the Source of Truth

The EP sets the authoritative classification at review time. `ep_classification` is a
required field on the EP review form. The proxy user entering the panel's decision must
always explicitly choose a classification, even if they are confirming the suggestion.
This removes any ambiguity about implicit confirmation.

`ep_classification_notes` is also required. There is no conditional — the proxy user
must always provide notes explaining the panel's classification decision.

______________________________________________________________________

## New Fields on `Curation`

The following fields are added to the `Curation` model.

**EP review fields** (all nullable, cleared when a curation is sent back):

| Field | Type | Notes | |---|---|---| | `ep_review_status` | CharField | Choices:
`not_started`, `needs_revision`, `approved` | | `ep_classification` | CharField |
Choices from `Classification` enum; set by EP | | `ep_classification_notes` | TextField
| Required at EP review time | | `ep_notes` | TextField | Optional overall notes from
the EP reviewer |

**Status transition timestamps** (auto-stamped, overwritten on re-entry):

| Field | Type | Set when | |---|---|---| | `in_progress_at` | DateTimeField | Curation
created, or sent back to In Progress | | `ready_for_review_at` | DateTimeField | Curator
submits for review | | `provisional_at` | DateTimeField | EP approves | | `published_at`
| DateTimeField | Curation is published |

All four timestamps are nullable and set automatically by the view that drives each
transition — they are never manually entered.

______________________________________________________________________

## New and Modified Views

### `curation_submit_for_review` (new)

A `@protected_view` function that accepts a POST with the curation slug. It checks that
the curation is `In Progress` and that all included evidence is `Done`, then transitions
the status to `Ready for Review`, stamps `ready_for_review_at`, and redirects to the
curation detail page. If the evidence check fails, it flashes an error and stays on the
detail page — the same guard that `validate_status` currently enforces when a curator
tries to mark a curation `Done`.

### `curation_ep_review` (new)

A `@ep_review_view` function that accepts a POST with the curation slug and the EP form
fields. Two paths:

- **Needs Revision**: sets `ep_review_status` to `needs_revision`, reverts the curation
  status to `In Progress`, stamps `in_progress_at`, clears all other EP fields
  (`ep_classification`, `ep_classification_notes`, `ep_notes`), and redirects to the
  curation detail page with an informational message.

- **Approved**: sets `ep_review_status` to `approved`, saves `ep_classification`,
  `ep_classification_notes`, and `ep_notes`, transitions the curation status to
  `Provisional`, stamps `provisional_at`, and redirects to the curation detail page with
  a success message.

### `curation_publish` (modified)

Currently checks `curation.status == Status.DONE`. This check changes to
`curation.status == Status.PROVISIONAL`. Everything else — the idempotency guard, the
`PublishedCuration.objects.create(...)` call, the redirect to `repo-detail` — stays the
same. When the `PublishedCuration` is created, `published_at` is also stamped on the
`Curation` instance.

______________________________________________________________________

## New URL Routes

Three new routes are added to `curation/urls.py`:

```
<slug:curation_slug>/submit-for-review  →  curation-submit-for-review
<slug:curation_slug>/ep-review          →  curation-ep-review
```

The existing `curation-publish` URL is unchanged.

______________________________________________________________________

## Forms

### `EPReviewForm` (new)

A `ModelForm` (or plain `Form`) with four fields:

- `ep_review_status` — radio or select, choices `needs_revision` / `approved`
- `ep_classification` — select, choices from `Classification` enum
- `ep_classification_notes` — textarea
- `ep_notes` — textarea, optional

The `clean()` method enforces that `ep_classification` and `ep_classification_notes` are
present when `ep_review_status` is `approved`. When `ep_review_status` is
`needs_revision`, `ep_classification` and `ep_classification_notes` are not required —
the view will clear them anyway.

### `CurationEditForm` (modified)

The `classification` field is removed. This form no longer exposes any classification
input to the curator.

______________________________________________________________________

## Templates

### `curation/partials/buttons.html` (modified)

The buttons shown on the curation detail page are now status-dependent:

```
In Progress:       [Edit]  [Edit Evidence]  [Submit for Review]
Ready for Review:  (EP reviewers only) [Review]
                   (all others) no action buttons; locked notice shown
Provisional:       [Publish to HLA Repo]
Published:         no action buttons
```

### `curation/detail.html` (modified)

The classification display changes. During `In Progress` and `Ready for Review`, the
page shows `suggested_classification` with a "Suggested" label. Once `ep_classification`
is set (i.e., after approval), it shows `ep_classification` as the authoritative value,
with `ep_classification_notes` and `ep_notes` shown in a collapsible section below.

### `curation/ep_review.html` (new)

A dedicated page for the EP review action, accessible only to users with
`has_ep_review_permissions`. Renders the `EPReviewForm` alongside a read-only summary of
the curation — status, score, and `suggested_classification` — so the reviewer has the
relevant context when filling in the EP fields.

______________________________________________________________________

## Validator Changes

`validate_classification` in `curation/validators/models/curation.py` is deleted
entirely. It validated the curator-chosen classification against the score, which is no
longer a thing the curator sets.

`validate_status` in the same file currently checks that all included evidence is `Done`
before a curation can be set to `Done`. It is updated to run the same check when the
status is being set to `Ready for Review` instead.

______________________________________________________________________

## Admin

`UserProfile` gains a `has_ep_review_permissions` checkbox in the Django admin,
alongside the existing `has_curation_permissions` checkbox. This is how EP reviewers are
designated.

______________________________________________________________________

## Open Questions

- Should the proxy user who performs the EP review also be the one who publishes, or can
  any `can_curate` user publish a `Provisional` curation? The current draft assumes any
  `can_curate` user can publish, since the EP approval is the meaningful gate.

- The `version` field on `PublishedCuration` is not addressed here. If versioning
  matters for the re-review case (a curation goes through two EP rounds before being
  published), it should be thought through separately.
