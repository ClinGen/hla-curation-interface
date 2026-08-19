# `curation`

The `curation` app is the core feature app of the HCI. It defines the `Curation` and
`Evidence` database models, implements the multistep HLA scoring framework, provides all
CRUD views and forms for curations and evidence records, manages the curation lifecycle
(In Progress → Ready for Review → Provisional → Published), and exposes templates for
listing, viewing, editing, reviewing, and auditing change history for both objects.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers `Curation`, `Demographic`, and `Evidence` with the Django admin using
`SimpleHistoryAdmin`; configures list display columns (including EP classification and
panel ID for curations), list filters, search fields, and read-only audit fields for
each model.

### `apps.py`

Django `AppConfig` for the `curation` app; sets the default auto field to `BigAutoField`
and registers the app under the name `curation`.

### `constants/__init__.py`

Empty file; marks this directory as a Python package.

### `constants/models/__init__.py`

Empty file; marks this directory as a Python package.

### `constants/models/common.py`

Defines the `Status` class with all lifecycle status codes (`IN_PROGRESS`, `DONE`,
`READY_FOR_REVIEW`, `PROVISIONAL`, `PUBLISHED`), plus `STATUS_CHOICES` (for evidence),
`CURATION_STATUS_CHOICES` (for the full curation lifecycle), and
`CURATION_STATUS_TRANSITIONS` (a dict encoding the allowed status transitions).

### `constants/models/curation.py`

Defines `CurationTypes` (allele/haplotype codes), `CURATION_TYPE_CHOICES`,
`Classification` (Definitive through Refuted codes), and `CLASSIFICATION_CHOICES` used
by the `Curation` model.

### `constants/models/evidence.py`

Defines all choice codes and display-name dicts used by the `Evidence` model:
`NumFields`, `Zygosity`, `TypingMethod`, `MultipleTestingCorrection`,
`EffectSizeStatistic`, `AdditionalPhenotypes`, and `PValueComparator`.

### `constants/score.py`

Defines the `Points` class with all numeric point values for each scoring step, and
instantiates `Step3AIntervals`, `Step3CIntervals`, and `Step4Intervals` — sets of
`Interval` objects encoding the p-value, effect size, and cohort size thresholds from
the HLA scoring framework.

### `constants/views.py`

Defines the `FRAMEWORK` list of dicts that drives the scoring matrix display; each dict
describes one row of the scoring table including its step label, category, associated
score property name, point value, operator, style, and layout flags (`split_horizontal`,
`split_vertical`).

### `fixtures/demographics.json`

Django fixture that seeds the `Demographic` model with the seven biogeographic groups
from Huddart et al. 2019 (American, East Asian, European, Central/South Asian, Near
Eastern, Oceanian, Sub-Saharan African).

### `fixtures/test_curations.json`

Django fixture providing a single `Curation` record (slug `C000001`, allele type, status
In Progress, classification Limited) for use in tests.

### `fixtures/test_evidence.json`

Django fixture providing a single `Evidence` record (slug `E000001`, linked to curation
pk=1 and publication pk=1) for use in tests.

### `forms.py`

Defines all Django form classes used by the curation app: `CurationCreateForm`,
`EPReviewForm` (a plain `Form` with decision, classification, evidence summary, notes,
and expert panel fields, requiring classification/summary/panel when the decision is
"approved"), `EvidenceCreateForm`, `EvidenceTopLevelEditForm` (and its formset factory),
and the detailed `EvidenceEditForm` covering all scoring fields with appropriate
widgets; `EvidenceEditForm.clean()` enforces that demographics are provided when the
typing method is imputation and that text quotes are provided when demographics are
entered.

### `interval.py`

Defines the `Interval` class, which represents a numeric interval with configurable
inclusive/exclusive bounds and a `contains()` method used during evidence scoring to
determine which scoring tier a p-value, effect size, or cohort size falls into.

### `models.py`

Defines the three database models: `Curation` (type, full lifecycle status, EP review
fields, `copied_from` self-FK, allele/haplotype/disease FKs, audit fields, `is_locked`
property, `can_submit()` validation method, `transition_to()` status-machine method,
`suggested_classification` property, and computed `score` property), `Demographic`
(biogeographic group name), and `Evidence` (all scoring data fields, FK to `Curation`
and `Publication`, `copy_to()` method, computed per-step score properties that delegate
to `score.py`, and change history via `simple_history`).

### `score.py`

Implements the per-step scoring functions (`get_step_1a_points` through
`get_step_6b_multiplier`) that translate an `Evidence` instance's field values into
numeric point contributions according to the HLA scoring framework; these functions are
called by the corresponding score properties on the `Evidence` model.

### `tables.py`

Defines `CurationTable`, a `django-tables2` `Table` subclass used by `CurationList`;
declares columns for slug (linked to curation detail), curation type, allele, haplotype,
disease, status, classification (showing EP classification when set, otherwise the
suggested classification), and updated date, with `render_status` producing styled Bulma
tags for each lifecycle state.

### `templates/curation/change.html`

Full-page template for viewing a single historical change to a `Curation` record;
includes a breadcrumb trail back to the curation's history page and embeds the shared
`common/history/change_body.html` partial.

### `templates/curation/create.html`

Full-page template for the Add Curation form; renders radio inputs for curation type and
searchable selects for allele, haplotype, and disease, and uses JavaScript to show or
hide the allele/haplotype field based on the selected curation type.

### `templates/curation/detail.html`

Full-page template for the curation detail view; shows status-specific notification
banners (locked warning for Ready for Review, approval notice for Provisional, read-only
notice with HLArepo link for Published, and EP classification notes when present), then
embeds the curation detail table partial, the action-button partial, and the evidence
summary table partial.

### `templates/curation/edit/evidence.html`

Full-page template for bulk-editing top-level evidence fields (status and included)
across all evidence in a curation via an inline formset table.

### `templates/curation/forms/curation.html`

Partial template that renders the curation edit form as a table, including read-only
fields (ID, allele/haplotype, disease, score, added date) alongside editable status and
classification selects.

### `templates/curation/forms/evidence.html`

Partial template that renders the `EvidenceTopLevelEditFormSet` as a table, displaying
each evidence record's ID, publication, needs-review flag, status, included checkbox,
and score.

### `templates/curation/history.html`

Full-page template for the curation change-history list; embeds the shared
`common/history/history_body.html` partial with the correct table ID and change URL
name.

### `templates/curation/list.html`

Full-page template for the curation search/list page; includes the
`curation/partials/table.html` DataTable partial and an "Add Curation" button.

### `templates/curation/partials/buttons.html`

Partial that renders the status-dependent action buttons on the curation detail page:
Add Evidence and Submit for Review when In Progress; a Review button (visible only to
reviewers) when Ready for Review; and a Publish to Repository button when Provisional;
no buttons are shown for Published curations.

### `templates/curation/partials/curation/detail_table.html`

Partial that renders a read-only summary table for a curation, showing its ID, allele or
haplotype, disease, status tag, classification tag, score, and added/updated dates, plus
a View History button.

### `templates/curation/partials/evidence/detail_table.html`

Partial that renders a collapsible evidence summary table on the curation detail page,
listing each evidence record's ID, publication, needs-review flag, status,
conflicting/included checkboxes, and score, with an Edit Evidence link when the curation
is not locked.

### `templates/curation/partials/table.html`

Partial that renders all curations as a DataTables-enhanced HTML table with columns for
ID, type, allele, haplotype, disease, status, classification, and updated date; used on
both the home page and the curation list page.

### `templates/curation/review.html`

Full-page template for the expert panel review form; renders the curation summary and
evidence tables for reference, then a form with fields for EP classification, evidence
summary, additional notes, expert panel, and an Approved/Needs Revision radio decision;
a JavaScript confirmation warns the reviewer if the chosen classification differs from
the suggested classification before submitting an approval.

### `templates/evidence/change.html`

Full-page template for viewing a single historical change to an `Evidence` record;
includes a breadcrumb trail through the curation and evidence detail and history pages,
and embeds `common/history/change_body.html`.

### `templates/evidence/create.html`

Full-page template for the Add Evidence form; renders a searchable publication select
and a Submit button, with breadcrumbs back to the parent curation.

### `templates/evidence/detail.html`

Full-page template for the evidence detail view; renders the evidence summary table,
then a tab bar toggling between the Data tab (all scored field values) and the Scoring
Matrix tab, with an Edit Data button when the curation is not locked.

### `templates/evidence/edit.html`

Full-page template for the evidence data-entry edit form; renders a sticky side-menu
linking to each scoring section and uses JavaScript to show only the relevant
effect-size input based on the selected statistic type.

### `templates/evidence/history.html`

Full-page template for the evidence change-history list; embeds the shared
`common/history/history_body.html` partial with the correct table ID, change URL name,
and both the curation and evidence slugs.

### `templates/evidence/partials/data.html`

Partial that renders all evidence scoring fields as a four-column table (Field, Status,
Value, Notes), using provided/not-provided tags to indicate whether each field has been
filled in.

### `templates/evidence/partials/detail_table.html`

Partial that renders a read-only summary table for an evidence record, showing its ID,
allele or haplotype, disease, publication, needs-review flag, status, and added/updated
dates, plus a View History button.

### `templates/evidence/partials/points.html`

Partial that renders the Points cell for a single scoring-matrix row; displays the point
value in a green success tag when the evidence's score for that step matches the row's
point value, and as plain text otherwise.

### `templates/evidence/partials/score.html`

Partial that renders the full scoring matrix table, iterating over the `FRAMEWORK` list
and delegating to `split_horizontal.html`, `split_vertical.html`, or `points.html`
sub-partials as needed; also shows footnotes about Step 3C.

### `templates/evidence/partials/split_horizontal.html`

Partial that renders a step category cell as a CSS grid when a step has side-by-side
GWAS/Non-GWAS category columns (e.g. Steps 3A and 4).

### `templates/evidence/partials/split_vertical.html`

Partial that renders a step category cell as a bullet list when a step has multiple
vertically stacked categories (e.g. Step 3C effect size thresholds).

### `templates/evidence/partials/step.html`

Partial that renders a status tag (in-progress or done) for a scoring step based on
whether the evidence's score for that step is `None`.

### `tests/__init__.py`

Empty file; marks this directory as a Python package.

### `tests/test_interval.py`

Unit tests for the `Interval` class, verifying boundary inclusivity/exclusivity behavior
for all four combinations of `start_inclusive` and `end_inclusive`.

### `tests/test_models.py`

Integration tests for the `Curation` and `Evidence` models, verifying default field
values, scoring property behavior as each field is set, preprint inclusion restrictions,
confidence interval scoring, and the p-value/has-association validation logic.

### `tests/test_validators.py`

Unit tests for `validators/common.py`'s `has_association_and_p_value_err_msg` function,
covering GWAS and non-GWAS p-value threshold boundary conditions.

### `tests/test_views.py`

Integration tests for all curation and evidence views (create, detail, edit, list,
history); verifies page rendering, form submission behavior, field persistence, and
score calculation using `ProtectedViewTestMixin`.

### `urls.py`

Defines all URL patterns for the curation app: create/detail/list routes for curations;
`edit-evidence`, `publish`, `submit`, `review`, and `copy` action routes for curations;
evidence create/detail/edit routes; and history/change routes for both curations and
evidence.

### `validators/__init__.py`

Empty file; marks this directory as a Python package.

### `validators/common.py`

Defines `has_association_and_p_value_err_msg`, a pure function shared by model and view
validators that returns an error message when `has_association=True` but the p-value is
absent or falls in the non-significant interval for GWAS or non-GWAS studies.

### `validators/models/__init__.py`

Empty file; marks this directory as a Python package.

### `validators/models/curation.py`

Defines model-level validators for the `Curation` model: `validate_status` (blocks
transitioning to Ready for Review if any included evidence is still in progress) and
`validate_curation_type` (ensures the correct allele or haplotype FK is set and clears
the unused FK).

### `validators/models/evidence.py`

Defines model-level validators for the `Evidence` model: p-value string parsing and
`Decimal` conversion, preprint publication inclusion checks, num-fields minimum
enforcement relative to the allele/haplotype resolution, effect-size statistic mutual
exclusivity, numeric string parsing for OR/RR/beta/CI fields, and the
has-association/p-value consistency check.

### `validators/views.py`

Defines view-level validation helpers called from `EvidenceEdit.form_valid`: mirrors the
model-level effect-size and has-association validators but operates on the cleaned form
data and adds errors to the form object rather than raising `ValidationError`, and
provides `maybe_to_decimal` conversion helpers that set the parsed `Decimal` fields on
the form instance.

### `views.py`

Defines all class-based and function-based views for the curation app: `CurationCreate`,
`CurationDetail`, `CurationList`, `CurationHistory`, `CurationChange`,
`curation_edit_evidence`, `curation_submit` (transitions curation to Ready for Review
after validating included evidence), `curation_review` (reviewer-only view that renders
the EP review form and transitions the curation to Provisional or back to In Progress),
`curation_publish` (transitions to Published and creates a `PublishedCuration` record),
`curation_copy` (clones a published curation and all its evidence into a new In Progress
curation), `EvidenceCreate`, `EvidenceDetail`, `EvidenceEdit`, `EvidenceHistory`, and
`EvidenceChange`; all views require authentication and curation permissions via
`ProtectedViewMixin` or `protected_view`/`reviewer_view` decorators.
