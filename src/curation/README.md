# `curation`

The core Django app for the HLA curation interface. It models and manages two primary
entities — `Curation` and `Evidence` — and implements the multi-step HLA scoring
framework used to classify HLA-disease associations. A curation targets either an allele
or a haplotype paired with a disease; evidence records capture the statistical and
methodological details from individual publications and are scored according to the
framework. The app also tracks biogeographic demographics, enforces validation rules at
both the model and view layer, and maintains a full change history via
`django-simple-history`.

### `__init__.py`

Empty package marker.

### `admin.py`

Registers `Curation`, `Demographic`, and `Evidence` with the Django admin site using
`SimpleHistoryAdmin`, which adds a change-history tab to each record's admin detail
page.

### `apps.py`

Declares the `CurationConfig` app configuration, setting `curation` as the app name and
`BigAutoField` as the default primary-key type.

### `constants/__init__.py`

Empty package marker.

### `constants/models/__init__.py`

Empty package marker.

### `constants/models/common.py`

Defines `Status` (with `IN_PROGRESS` and `DONE` codes) and the corresponding
`STATUS_CHOICES` dict used by both the `Curation` and `Evidence` models.

### `constants/models/curation.py`

Defines `CurationTypes` (`ALLELE` / `HAPLOTYPE`), `Classification` (Definitive, Strong,
Moderate, Limited, No Known, Disputed, Refuted), and their associated `*_CHOICES` dicts
used as field choices on the `Curation` model.

### `constants/models/evidence.py`

Defines all enumeration classes and their `*_CHOICES` dicts used as field choices on the
`Evidence` model: `NumFields`, `Zygosity`, `TypingMethod`, `MultipleTestingCorrection`,
`EffectSizeStatistic`, `AdditionalPhenotypes`, and `PValueComparator`.

### `constants/score.py`

Defines `Points` (all numeric point values for the 6-step scoring framework) and three
interval-set classes — `Step3AIntervals`, `Step3CIntervals`, and `Step4Intervals` —
instantiated together in `Intervals`. Used by `score.py` and `constants/views.py`.

### `constants/views.py`

Defines `FRAMEWORK`, a list of dicts that describes every row of the scoring matrix
table rendered on the evidence detail page. Each entry specifies step text, category
labels, the evidence property to read for the current score, point values, operators,
and display styling.

### `fixtures/demographics.json`

Seed fixture containing the biogeographic groups from Huddart et al. 2019 (e.g.,
African, East Asian, European). Load once with `python manage.py loaddata demographics`.

### `fixtures/test_curations.json`

Test fixture providing a sample `Curation` record (pk=1, allele curation for
`A*01:02:03` / acute oran berry intoxication) used by model, validator, and view tests.

### `fixtures/test_evidence.json`

Test fixture providing a sample `Evidence` record (pk=1, `E000001`) linked to the
curation in `test_curations.json`, used by view tests.

### `forms.py`

Defines all Django `ModelForm` classes for the app:

- `CurationCreateForm` — type, allele/haplotype, and disease fields for creating a
  curation.
- `CurationEditForm` — status and classification fields for editing a curation.
- `EvidenceCreateForm` — publication field for adding evidence to a curation.
- `EvidenceTopLevelEditForm` / `EvidenceTopLevelEditFormSet` — status, conflicting, and
  included flags for bulk-editing evidence from the curation detail page.
- `EvidenceEditForm` — all scoring-related fields for the evidence edit page; includes a
  `clean()` that enforces demographics when typing method is imputation.

### `interval.py`

Defines the `Interval` class, a utility for representing a numeric interval with
configurable inclusive/exclusive bounds. Exposes `contains(number)` for membership
checks. Used by `constants/score.py` to define p-value, effect-size, and cohort-size
scoring intervals.

### `models.py`

Defines the three database models:

- `Curation` — links an allele or haplotype to a disease, holds status and
  classification, auto-generates a `C######` slug, and exposes a `score` property that
  sums included (non-conflicting) evidence scores.
- `Demographic` — a reference list of biogeographic groups (seeded from
  `fixtures/demographics.json`).
- `Evidence` — captures all scoring inputs for one publication: GWAS flag, allele
  resolution, zygosity, phase, typing method, demographics, p-value (stored as both a
  raw string and a parsed `Decimal`), multiple-testing correction, effect-size statistic
  with OR/RR/beta values, confidence interval, cohort size, additional phenotypes, and
  association/protective flags. Exposes `score` and per-step `score_step_*` properties
  that delegate to `score.py`.

### `score.py`

Implements the HLA scoring framework as pure functions that accept an `Evidence`
instance. One function per scoring step (1A–1D, 2, 3A, 3B, 3C1, 3C2, 4, 5, 6A
multiplier, 6B multiplier); results are consumed by the corresponding `score_step_*`
properties on `Evidence`.

### `templates/curation/change.html`

Detail page for a single historical change record on a curation, showing which fields
changed between two history snapshots.

### `templates/curation/create.html`

Form page for creating a new curation (type, allele/haplotype, disease).

### `templates/curation/detail.html`

Read-only detail page for a curation, displaying its metadata and a table of all
associated evidence records with their top-level status, scores, and action links.

### `templates/curation/edit/curation.html`

Form page for editing a curation's status and classification.

### `templates/curation/edit/evidence.html`

Form page for bulk-editing the top-level fields of all evidence records belonging to a
curation (status, conflicting, included).

### `templates/curation/forms/curation.html`

Reusable partial rendering the curation create/edit form fields.

### `templates/curation/forms/evidence.html`

Reusable partial rendering the evidence top-level edit formset fields.

### `templates/curation/history.html`

Page listing the full change history for a curation, with links to individual change
records.

### `templates/curation/list.html`

Searchable list of all curations, showing ID, type, allele/haplotype, disease, status,
classification, and last-updated date.

### `templates/curation/partials/buttons.html`

Reusable partial rendering the action buttons (Edit, Add Evidence, Publish, etc.) shown
on the curation detail page.

### `templates/curation/partials/curation/detail_table.html`

Partial rendering the metadata table (type, allele/haplotype, disease, status,
classification, score) on the curation detail page.

### `templates/curation/partials/evidence/detail_table.html`

Partial rendering the evidence summary table within the curation detail page.

### `templates/curation/partials/table.html`

Reusable partial for a generic sortable/filterable table used on the curation list page.

### `templates/evidence/change.html`

Detail page for a single historical change record on an evidence item, showing
field-level diffs between two history snapshots.

### `templates/evidence/create.html`

Form page for adding a new evidence record to a curation (publication selection only).

### `templates/evidence/detail.html`

Detail page for an evidence record, with tabbed navigation between the data view and the
scoring matrix.

### `templates/evidence/edit.html`

Form page for editing all scoring-related fields of an evidence record.

### `templates/evidence/history.html`

Page listing the full change history for an evidence record, with links to individual
change records.

### `templates/evidence/partials/data.html`

Partial rendering the "Data" tab content on the evidence detail page — all captured
field values displayed in a structured layout.

### `templates/evidence/partials/detail_table.html`

Partial rendering the top-level metadata table (publication, status, conflicting,
included) on the evidence detail page.

### `templates/evidence/partials/points.html`

Partial rendering the points value cell within a scoring matrix row.

### `templates/evidence/partials/score.html`

Partial rendering a single row of the scoring matrix table (step label, category,
current score highlight, points, operator).

### `templates/evidence/partials/split_horizontal.html`

Partial rendering a matrix row whose category is split horizontally between GWAS and
non-GWAS columns (used for steps 3A and 4).

### `templates/evidence/partials/split_vertical.html`

Partial rendering a matrix row whose category is split vertically to show multiple
effect-size interval bands side by side (used for step 3C).

### `templates/evidence/partials/step.html`

Partial rendering a standard (non-split) scoring matrix row.

### `tests/__init__.py`

Empty package marker.

### `tests/test_interval.py`

Unit tests for `interval.Interval`, covering inclusive, exclusive, and mixed-bound
`contains()` behavior at boundaries and midpoints.

### `tests/test_models.py`

Integration tests for `Curation` and `Evidence` model behavior: default field values,
scoring increases when each scoring-step field is set, p-value significance thresholds,
preprint inclusion rules, and `num_fields` resolution validation against allele and
haplotype field counts.

### `tests/test_validators.py`

Unit tests for `validators/common.py`, specifically
`has_association_and_p_value_err_msg`, verifying that the function correctly identifies
significant vs. insignificant p-values for both GWAS and non-GWAS contexts.

### `tests/test_views.py`

Integration tests for all curation and evidence views: access control (via
`ProtectedViewTestMixin`), template selection, expected page text, form submission
success/failure, and scoring output on the evidence detail page.

### `urls.py`

URL configuration for the curation app, mapping slug-based paths to create, detail,
list, edit, publish, history, and change views for both `Curation` and `Evidence`.

### `validators/__init__.py`

Empty package marker.

### `validators/common.py`

Shared validator logic: `has_association_and_p_value_err_msg` returns an error message
if `has_association=True` but the p-value is above the significance threshold (GWAS:
1e-4; non-GWAS: 0.05) or absent. Used by both model and view validators.

### `validators/models/__init__.py`

Empty package marker.

### `validators/models/curation.py`

Model-layer validators for `Curation`: `validate_status` (blocks marking done if
included evidence is still in progress), `validate_curation_type` (requires allele for
allele curations, haplotype for haplotype curations, and clears the unused FK), and
`validate_classification` (enforces score ranges for each classification tier).

### `validators/models/evidence.py`

Model-layer validators for `Evidence`: validates the p-value string format and parses it
to a `Decimal`, enforces significance rules for `has_association`, validates numeric
strings for OR/RR/beta/CI fields, prevents preprint publications from being included,
and enforces that `num_fields` does not exceed the resolution of the linked allele or
haplotype.

### `validators/views.py`

View-layer validators for `EvidenceEdit`: mirrors the model validators but operates on
cleaned form data. Sets parsed `Decimal` values for OR, RR, beta, CI start/end on the
form instance, clears unused effect-size fields based on the selected statistic, and
adds form errors for `has_association` / p-value conflicts.

### `views.py`

All Django views for the app:

- `CurationCreate`, `CurationDetail`, `CurationEdit`, `CurationList` — standard
  class-based views for CRUD on curations.
- `curation_edit_evidence` — function-based view for bulk-editing evidence top-level
  fields.
- `curation_publish` — publishes a done curation to the repository by creating a
  `PublishedCuration` record; blocks if already published or not done.
- `EvidenceCreate`, `EvidenceDetail`, `EvidenceEdit` — class-based views for evidence;
  `EvidenceEdit` blocks edits when the parent curation is published and runs view-layer
  validators in `form_valid`.
- `CurationHistory`, `CurationChange`, `EvidenceHistory`, `EvidenceChange` — read-only
  history and diff views backed by `django-simple-history`.
