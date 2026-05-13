# `curation`

This directory contains the `curation` Django app for the HLA Curation Interface
(HCI). The app is the core of the system: it lets curators create curations
(for either an allele or a haplotype, paired with a disease), attach `Evidence`
records drawn from publications, and score that evidence against the HLA
scoring framework. Score properties on `Evidence` and `Curation` aggregate the
inputs into a per-evidence score and a per-curation total, and a
`curation_publish` view promotes "Done" curations into the read-only
repository.

### `__init__.py`

Marks the directory as a Python package.

### `admin.py`

Registers the `Curation` and `Evidence` models with Django's admin site and
configures their list displays, filters, search fields, and read-only fields.

### `apps.py`

Django `AppConfig` for the `curation` app.

### `constants/__init__.py`

Marks the directory as a Python package.

### `constants/models/__init__.py`

Marks the directory as a Python package.

### `constants/models/common.py`

Defines `Status` and its `STATUS_CHOICES` tuple, shared between the `Curation`
and `Evidence` models.

### `constants/models/curation.py`

Defines the `CurationTypes` and `Classification` enums (and their
`*_CHOICES` tuples) used by the `Curation` model.

### `constants/models/evidence.py`

Defines the enums and choice tuples used by the `Evidence` model: `Zygosity`,
`TypingMethod`, `MultipleTestingCorrection`, `EffectSizeStatistic`,
`AdditionalPhenotypes`, and their corresponding `*_CHOICES` tuples.

### `constants/score.py`

Defines the `Points` and `Intervals` constants consumed by `score.py` when
computing per-step points for an `Evidence` record.

### `constants/views.py`

Defines the `FRAMEWORK` data structure that drives the evidence detail
template's scoring breakdown.

### `fixtures/demographics.json`

Django fixture containing the Huddart et al. 2019 biogeographic groups used to
populate the `Demographic` model.

### `fixtures/test_curations.json`

Django fixture containing test `Curation` records used by the test suite.

### `fixtures/test_evidence.json`

Django fixture containing test `Evidence` records used by the test suite.

### `forms.py`

`ModelForm` classes for the views: `CurationCreateForm`, `CurationEditForm`,
`EvidenceCreateForm`, `EvidenceTopLevelEditForm` (plus
`EvidenceTopLevelEditFormSet` for editing all of a curation's evidence in one
screen), and `EvidenceEditForm` (the large per-evidence scoring form, with a
`clean()` rule requiring demographics when the typing method is imputation).

### `interval.py`

Defines the `Interval` class used by the scoring code. Supports
inclusive/exclusive bounds, infinite endpoints, a `contains` membership check,
and human- and developer-readable string forms.

### `models.py`

Defines the app's database models: `Curation` (status, curation type,
classification, allele/haplotype/disease foreign keys, and a `score` property
that sums included evidence), `Demographic` (the biogeographic groups from
Huddart et al. 2019, loadable from the `demographics.json` fixture), and
`Evidence` (the large per-publication record with all scoring inputs,
`num_fields` and `score` properties, and `score_step_*` properties that
delegate to `score.py`).

### `score.py`

Pure functions that compute points for each step of the HLA scoring framework
given an `Evidence` instance: `get_step_1a_points` through
`get_step_5_points`, plus the `get_step_6a_multiplier` and
`get_step_6b_multiplier` multipliers applied to the summed step points.

### `templates/curation/create.html`

HTML template that renders the curation creation form for the `CurationCreate`
view.

### `templates/curation/detail.html`

HTML template that renders the curation detail page for the `CurationDetail`
view, including the curation's evidence list and aggregate score.

### `templates/curation/edit/curation.html`

HTML template that renders the curation edit form for the `CurationEdit` view.

### `templates/curation/edit/evidence.html`

HTML template that renders the formset-based bulk edit page for all of a
curation's evidence, used by the `curation_edit_evidence` view.

### `templates/curation/forms/curation.html`

Shared form fragment for the curation create and edit pages.

### `templates/curation/forms/evidence.html`

Shared form fragment for the evidence create and top-level edit pages.

### `templates/curation/list.html`

HTML template that renders the paginated curation list for the `CurationList`
view.

### `templates/curation/partials/buttons.html`

Reusable partial that renders the action buttons (edit, edit evidence,
publish) shown on the curation detail page.

### `templates/curation/partials/curation/detail_table.html`

Reusable partial that renders the table summarizing a curation's top-level
fields on the curation detail page.

### `templates/curation/partials/evidence/detail_table.html`

Reusable partial that renders the table summarizing an evidence record's
top-level fields on the curation detail page.

### `templates/curation/partials/table.html`

Reusable partial that renders the curation list table.

### `templates/evidence/create.html`

HTML template that renders the evidence creation form for the
`EvidenceCreate` view.

### `templates/evidence/detail.html`

HTML template that renders the evidence detail page for the `EvidenceDetail`
view, including the full scoring breakdown.

### `templates/evidence/edit.html`

HTML template that renders the large per-evidence scoring form for the
`EvidenceEdit` view.

### `templates/evidence/partials/data.html`

Reusable partial that renders a single labeled data row inside the evidence
detail scoring breakdown.

### `templates/evidence/partials/detail_table.html`

Reusable partial that renders the evidence detail summary table.

### `templates/evidence/partials/points.html`

Reusable partial that renders the points awarded for one step of the scoring
framework on the evidence detail page.

### `templates/evidence/partials/score.html`

Reusable partial that renders an evidence record's total score on the evidence
detail page.

### `templates/evidence/partials/split_horizontal.html`

Reusable partial that renders a horizontally split row in the evidence detail
scoring breakdown.

### `templates/evidence/partials/split_vertical.html`

Reusable partial that renders a vertically split row in the evidence detail
scoring breakdown.

### `templates/evidence/partials/step.html`

Reusable partial that renders a single step of the scoring framework on the
evidence detail page.

### `tests/__init__.py`

Marks the directory as a Python package.

### `tests/test_interval.py`

Tests for the `Interval` class in `interval.py`.

### `tests/test_models.py`

Tests for the `Curation`, `Demographic`, and `Evidence` models, including
the per-step and aggregate scoring logic.

### `tests/test_validators.py`

Tests for the model- and view-level validators in the `validators/` package.

### `tests/test_views.py`

Tests for the app's views, including the publish flow and the rules that lock
editing once a curation has been published.

### `urls.py`

URL routes for the app: `curation-create`, `curation-detail`, `curation-list`,
`curation-edit`, `curation-edit-evidence`, `curation-publish`,
`evidence-create`, `evidence-detail`, and `evidence-edit`.

### `validators/__init__.py`

Marks the directory as a Python package.

### `validators/common.py`

Helper functions shared between the model- and view-level validators, such as
the message builder for the has-association / p-value consistency check.

### `validators/models/__init__.py`

Marks the directory as a Python package.

### `validators/models/curation.py`

Model-level `clean()` validators for the `Curation` model.

### `validators/models/evidence.py`

Model-level `clean()` validators for the `Evidence` model.

### `validators/views.py`

View-level validators called from `EvidenceEdit.form_valid`, including
`validate_effect_size_statistic` (clears the unused effect-size fields based
on the selected statistic), `validate_has_association_and_p_value`, and
helpers that parse the odds-ratio, relative-risk, beta, and confidence
interval string fields into `Decimal` values on the model instance.

### `views.py`

Class- and function-based views for the app: `CurationCreate`, `CurationDetail`,
`CurationEdit`, `curation_edit_evidence` (formset-based bulk edit of a
curation's evidence), `curation_publish` (creates a `PublishedCuration` for a
"Done" curation), `EvidenceCreate`, `EvidenceDetail`, `EvidenceEdit`, and
`CurationList`. Edit views block changes once a curation has been published.
All views inherit from `ProtectedViewMixin` or use `@protected_view`.
