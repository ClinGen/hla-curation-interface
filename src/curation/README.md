# `curation`

The core Django app for the HLA Curation Interface. It manages the full lifecycle of HLA curations (allele- and haplotype-based) and their associated evidence items, including creation, editing, submission for expert panel review, approval, and publication to the repository. The app implements a multi-step evidence scoring framework that maps study-level data (typing method, p-value, cohort size, effect size, etc.) to a numeric score that drives a suggested classification.

### `__init__.py`

Empty file that marks the directory as a Python package.

### `admin.py`

Registers the `Curation`, `Demographic`, and `Evidence` models with the Django admin site using `SimpleHistoryAdmin`, exposing list display columns, filters, and search fields for each model.

### `apps.py`

Defines the `CurationConfig` app configuration class, which sets the app name to `curation` and specifies `BigAutoField` as the default primary key type.

### `constants/__init__.py`

Empty file that marks the `constants` directory as a Python package.

### `constants/models/__init__.py`

Empty file that marks the `constants/models` directory as a Python package.

### `constants/models/common.py`

Defines the `Status` class with lifecycle status codes shared by `Curation` and `Evidence` (`IN_PROGRESS`, `DONE`, `READY_FOR_REVIEW`, `PROVISIONAL`, `PUBLISHED`), along with the allowed status choice dicts and the `CURATION_STATUS_TRANSITIONS` mapping that enforces valid status progressions.

### `constants/models/curation.py`

Defines the `CurationTypes` class (`ALLELE`, `HAPLOTYPE`) and the `Classification` class (e.g., `DEFINITIVE`, `STRONG`, `MODERATE`, `LIMITED`), along with their corresponding human-readable choice dicts used by the `Curation` model.

### `constants/models/evidence.py`

Defines choice classes and dicts used by the `Evidence` model, covering allele resolution (`NumFields`), zygosity (`Zygosity`), HLA typing method (`TypingMethod`), multiple testing correction (`MultipleTestingCorrection`), effect size statistic (`EffectSizeStatistic`), additional phenotypes (`AdditionalPhenotypes`), and p-value comparator (`PValueComparator`).

### `constants/score.py`

Defines the `Points` class with all point values for the scoring framework's steps 1A through 6B, and instantiates `Step3AIntervals`, `Step3CIntervals`, and `Step4Intervals` classes that set up `Interval` objects for p-value, effect size, and cohort size scoring thresholds (GWAS and non-GWAS variants). These are collected under the top-level `Intervals` class.

### `constants/views.py`

Defines the `FRAMEWORK` list, a structured data representation of every row in the HLA scoring matrix (steps 1A–6B). Each entry carries display metadata (step text, category, point value, operator, style, split layout flags) and the name of the `Evidence` property that holds that step's computed score; this list is consumed by the scoring matrix template.

### `fixtures/demographics.json`

A Django fixture containing the seven biogeographic `Demographic` groups defined by Huddart et al. 2019 (e.g., American, East Asian, European). Load with `python manage.py loaddata demographics.json` to seed the database.

### `fixtures/test_curations.json`

A Django fixture with a single minimal in-progress allele curation (`C000001`) for use in tests that require a pre-existing `Curation` instance.

### `fixtures/test_evidence.json`

A Django fixture with a single minimal in-progress evidence item (`E000001`) linked to the test curation, used in tests that require a pre-existing `Evidence` instance.

### `forms.py`

Defines the Django forms used by curation and evidence views: `CurationCreateForm` (create a curation), `EPReviewForm` (expert panel review with decision, classification, and notes), `EvidenceCreateForm` (attach a publication), `EvidenceTopLevelEditForm` / `EvidenceTopLevelEditFormSet` (inline status/inclusion editing from the curation detail page), and `EvidenceEditForm` (the full step-by-step evidence data entry form with cross-field validation).

### `interval.py`

Defines the `Interval` class, a small utility that represents a numeric interval with configurable inclusive/exclusive bounds and a `contains(number)` method. It also provides human-readable `__str__` and developer-oriented `__repr__` representations. Used throughout the scoring module to test whether p-values, effect sizes, and cohort sizes fall within scoring thresholds.

### `models.py`

Defines the three core database models for the app. `Curation` tracks an allele or haplotype paired with a disease, manages lifecycle status transitions, stores expert panel review fields, and computes an aggregate score from its included evidence. `Demographic` holds the biogeographic population groups. `Evidence` stores all study-level data fields (typing method, p-value, effect size, cohort size, etc.) and exposes per-step score properties that feed into the HLA scoring framework; all three models use `simple_history` for change tracking.

### `score.py`

Implements the per-step point-calculation functions (`get_step_1a_points` through `get_step_6b_multiplier`) that are called by the `Evidence` model's score properties. Each function takes an `Evidence` instance and returns the numeric points (or `None` if insufficient data) for its corresponding framework step.

### `tables.py`

Defines the `CurationTable` class (using `django-tables2`) that renders the curation list view, including a linked slug column, type, allele/haplotype, disease, a badge-rendered status column, and a classification column that shows the EP classification if set or the computed suggested classification otherwise.

### `templates/curation/change.html`

Full-page template for viewing a single historical change record on a curation. Renders breadcrumb navigation and delegates the diff body to the shared `common/history/change_body.html` partial.

### `templates/curation/create.html`

Full-page template for the "Add Curation" form. Renders radio inputs for curation type and searchable selects for allele/haplotype and disease, and includes JavaScript that shows or hides the allele and haplotype fields based on the selected curation type.

### `templates/curation/detail.html`

Full-page template for viewing a curation's details. Displays status banners (locked, ready for review, provisional, published), EP classification notes when present, the curation detail table partial, the action buttons partial, and the evidence list partial.

### `templates/curation/edit/evidence.html`

Full-page template for the curation-level evidence editing view. Renders the curation detail table, action buttons, and the inline evidence formset partial (`curation/forms/evidence.html`) that allows bulk status and inclusion changes.

### `templates/curation/forms/evidence.html`

Reusable partial that renders the inline evidence formset table on the curation edit-evidence page, including columns for ID, publication, needs-review flag, editable status and inclusion fields, and the computed score for each evidence item.

### `templates/curation/history.html`

Full-page template for the curation history list view. Renders breadcrumb navigation and delegates the history table body to the shared `common/history/history_body.html` partial.

### `templates/curation/list.html`

Full-page template for the curation search/list page. Renders a search input, a paginated results area, and an "Add Curation" button.

### `templates/curation/partials/buttons.html`

Partial that renders the context-sensitive action buttons on the curation detail page: "Add Evidence" and "Submit for Review" when in progress, "Review" (for reviewers) when ready for review, and "Publish to Repository" when provisional.

### `templates/curation/partials/curation/detail_table.html`

Partial that renders a summary table for a `Curation` object, showing its ID, allele or haplotype, disease, status badge, EP or suggested classification, aggregate score, and timestamps, plus a "View History" button.

### `templates/curation/partials/evidence/detail_table.html`

Partial that renders a read-only summary table listing all evidence items belonging to a curation, with columns for ID, publication, needs-review flag, status, inclusion checkbox, and score.

### `templates/curation/review.html`

Full-page template for the expert panel review form. Displays the curation summary and evidence table, then renders the `EPReviewForm` fields (classification, evidence summary, notes, expert panel selector, and approve/needs-revision decision). Includes JavaScript that warns the reviewer if the selected classification differs from the system-suggested one.

### `templates/evidence/change.html`

Full-page template for viewing a single historical change record on an evidence item. Renders breadcrumb navigation (including the parent curation) and delegates the diff body to the shared `common/history/change_body.html` partial.

### `templates/evidence/create.html`

Full-page template for adding a new evidence item to a curation. Renders a searchable publication select and a submit button within the curation's breadcrumb context.

### `templates/evidence/detail.html`

Full-page template for viewing an evidence item's details. Renders the evidence summary table, a tab bar for switching between the "Data" view (`evidence/partials/data.html`) and the "Scoring Matrix" view (`evidence/partials/score.html`), and an "Edit Data" button when the curation is unlocked.

### `templates/evidence/edit.html`

Full-page template for the evidence data editing form. Renders the evidence summary table, a sidebar navigation menu, and sectioned form fields for all scoring steps (GWAS flag, allele resolution, zygosity, phase, typing method, demographics, p-value, multiple testing correction, effect size, confidence interval, cohort size, additional phenotypes, significant association, protective flag, and needs-review flag). Includes JavaScript that shows/hides effect size sub-fields based on the selected statistic type.

### `templates/evidence/history.html`

Full-page template for the evidence history list view. Renders breadcrumb navigation including the parent curation, and delegates the history table body to the shared `common/history/history_body.html` partial.

### `templates/evidence/partials/data.html`

Partial that renders a read-only table of all curated data fields for an `Evidence` object, with "Provided" or "Not Provided" status tags for optional fields and the stored value and curator notes for each field.

### `templates/evidence/partials/detail_table.html`

Partial that renders a brief summary table for an `Evidence` object, showing its ID, the parent curation's allele/haplotype and disease, the linked publication, needs-review flag, status, and timestamps, plus a "View History" button.

### `templates/evidence/partials/points.html`

Partial that renders the points cell for a single scoring matrix row. Highlights the cell with a green success badge when the evidence's computed score for that step matches the row's point value, otherwise renders the value as plain text.

### `templates/evidence/partials/score.html`

Partial that renders the full HLA scoring matrix table for an evidence item, iterating over the `FRAMEWORK` list and including the `step.html`, `split_horizontal.html`, and `split_vertical.html` partials as needed for each row, plus footnotes about Step 3C.

### `templates/evidence/partials/split_horizontal.html`

Partial that renders a step category cell containing multiple sub-categories in a horizontal grid layout (used for steps that have parallel GWAS and non-GWAS columns, such as steps 3A and 4).

### `templates/evidence/partials/split_vertical.html`

Partial that renders a step category cell containing multiple sub-categories as a vertical list (used for step 3C's OR/RR and Beta interval categories).

### `templates/evidence/partials/step.html`

Partial that renders the completion-status indicator for a scoring step, showing an "In Progress" tag when the evidence's score for that step is `None` and a "Done" tag when it has been computed.

### `tests/__init__.py`

Empty file that marks the `tests` directory as a Python package.

### `tests/test_interval.py`

Unit tests for the `Interval` class, verifying boundary inclusion and exclusion behavior for all four combinations of inclusive/exclusive lower and upper bounds using the standard `unittest.TestCase`.

### `tests/test_models.py`

Integration tests for the `Curation` and `Evidence` models. Tests cover default field values, score calculation for every scoring step (including GWAS vs. non-GWAS variants and the p-value comparator edge case), suggested classification thresholds, curation copying, and validation rules for publication type inclusion, allele resolution minimums, and the significant association/p-value consistency check.

### `tests/test_validators.py`

Unit tests for the `has_association_and_p_value_err_msg` helper in `validators/common.py`, verifying that it correctly identifies insignificant p-values (at and above the GWAS/non-GWAS thresholds) and passes significant ones for both GWAS and non-GWAS study types.

### `tests/test_views.py`

Integration tests for all curation and evidence views, covering HTTP status codes, template rendering, expected page content, authentication/authorization enforcement (via `ProtectedViewTestMixin`), and end-to-end form submission behavior for create, edit, submit, review, publish, copy, history, and change views.

### `urls.py`

Defines the URL patterns for the curation app, mapping slug-based paths to all curation and evidence views: create, detail, list, edit-evidence, submit, review, publish, copy, evidence create/detail/edit, and history/change views for both curations and evidence items.

### `validators/__init__.py`

Empty file that marks the `validators` directory as a Python package.

### `validators/common.py`

Provides the `has_association_and_p_value_err_msg` helper function, which returns an error message string (or `None`) when `has_association=True` is set but the supplied p-value is missing or falls in the statistically insignificant range for the given study type (GWAS or non-GWAS).

### `validators/models/__init__.py`

Empty file that marks the `validators/models` directory as a Python package.

### `validators/models/curation.py`

Defines `validate_status` (blocks status transitions that would require included evidence to still be in progress) and `validate_curation_type` (ensures an allele curation has an allele and a haplotype curation has a haplotype, and clears the irrelevant FK). Both are called from `Curation.clean()`.

### `validators/models/evidence.py`

Defines field-level validation functions called from `Evidence.clean()`, including p-value string parsing with comparator extraction, numeric string-to-Decimal conversion for effect size and CI fields, preprint publication inclusion prevention, allele resolution minimum enforcement, and the `has_association`/p-value consistency check.

### `validators/views.py`

Defines view-layer validation helpers called from `EvidenceEdit.form_valid()` after Django form cleaning: enforces mutual exclusivity of effect size statistic fields, converts string inputs to `Decimal` values on the form instance for OR/RR/beta/CI fields, and re-validates the has-association/p-value consistency using the cleaned form data.

### `views.py`

Implements all view classes and functions for the curation app: `CurationCreate`, `CurationDetail`, `CurationList`, `curation_edit_evidence`, `curation_submit`, `curation_review`, `curation_publish`, `curation_copy`, `EvidenceCreate`, `EvidenceDetail`, `EvidenceEdit`, `CurationHistory`, `CurationChange`, `EvidenceHistory`, and `EvidenceChange`. Views enforce authentication and (where applicable) reviewer permissions, respect the curation locked state, and handle status transitions atomically.
