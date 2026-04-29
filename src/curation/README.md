# Curation

This directory contains the `curation` Django app for the HLA Curation Interface
(HCI). The app is the core of the system: it lets curators create curations
(for either an allele or a haplotype, paired with a disease), attach `Evidence`
records drawn from publications, and score that evidence against the HLA
scoring framework. Each `Evidence` record captures the study design and
statistics needed by the framework (GWAS status, zygosity, phase confirmation,
typing method, demographics, p-value, multiple-testing correction, effect-size
statistic with odds ratio / relative risk / beta and confidence interval,
cohort size, additional phenotypes, association direction, protective status,
and review flags). Score properties on `Evidence` and `Curation` aggregate
these inputs into a per-evidence score and a per-curation total, and a
`curation_publish` view promotes "Done" curations into the read-only
repository.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers the `Curation` and `Evidence` models with Django's
  admin site and configures their list displays, filters, search fields, and
  read-only fields.
- `apps.py` — Django `AppConfig` for the `curation` app.
- `forms.py` — `ModelForm` classes for the views: `CurationCreateForm`,
  `CurationEditForm`, `EvidenceCreateForm`, `EvidenceTopLevelEditForm` (plus
  `EvidenceTopLevelEditFormSet` for editing all of a curation's evidence in
  one screen), and `EvidenceEditForm` (the large per-evidence scoring form,
  with a `clean()` rule requiring demographics when the typing method is
  imputation).
- `interval.py` — Defines the `Interval` class used by the scoring code.
  Supports inclusive/exclusive bounds, infinite endpoints, a `contains`
  membership check, and human- and developer-readable string forms.
- `models.py` — Defines the app's database models: `Curation` (status,
  curation type, classification, allele/haplotype/disease foreign keys, and a
  `score` property that sums included evidence), `Demographic` (the
  biogeographic groups from Huddart et al. 2019, loadable from the
  `demographics.json` fixture), and `Evidence` (the large per-publication
  record with all scoring inputs, `num_fields` and `score` properties, and
  `score_step_*` properties that delegate to `score.py`).
- `score.py` — Pure functions that compute points for each step of the HLA
  scoring framework given an `Evidence` instance: `get_step_1a_points`
  through `get_step_5_points`, plus the `get_step_6a_multiplier` and
  `get_step_6b_multiplier` multipliers applied to the summed step points.
- `urls.py` — URL routes for the app: `curation-create`, `curation-detail`,
  `curation-list`, `curation-edit`, `curation-edit-evidence`,
  `curation-publish`, `evidence-create`, `evidence-detail`, and
  `evidence-edit`.
- `views.py` — Class- and function-based views for the app: `CurationCreate`,
  `CurationDetail`, `CurationEdit`, `curation_edit_evidence` (formset-based
  bulk edit of a curation's evidence), `curation_publish` (creates a
  `PublishedCuration` for a "Done" curation), `EvidenceCreate`,
  `EvidenceDetail`, `EvidenceEdit`, and `CurationList`. Edit views block
  changes once a curation has been published. All views inherit from
  `ProtectedViewMixin` or use `@protected_view`.

## Subdirectories

- `constants/` — Enum-style constants and choice tuples used by models,
  views, and the scoring code:
  - `models/common.py`, `models/curation.py`, `models/evidence.py` —
    `Status`, `CurationTypes`, `Classification`, `Zygosity`, `TypingMethod`,
    `MultipleTestingCorrection`, `EffectSizeStatistic`,
    `AdditionalPhenotypes`, etc., with their corresponding `*_CHOICES`
    tuples.
  - `score.py` — `Points` and `Intervals` used by `score.py`.
  - `views.py` — The `FRAMEWORK` structure consumed by the evidence detail
    template.
- `fixtures/` — JSON fixtures: `demographics.json` (the Huddart et al. 2019
  biogeographic groups) and `test_curations.json` / `test_evidence.json`
  (test data).
- `migrations/` — Django database migrations for the `Curation`, `Evidence`,
  and `Demographic` models.
- `services/` — Currently empty (only stale `__pycache__` artifacts remain
  from a previous `workflow` module).
- `templates/curation/` — HTML templates for curation pages: `create.html`,
  `detail.html`, `list.html`, `edit/curation.html` and `edit/evidence.html`,
  shared form fragments under `forms/`, and reusable partials (`buttons.html`,
  `table.html`, plus `curation/` and `evidence/` partial subdirectories).
- `templates/evidence/` — HTML templates for evidence pages: `create.html`,
  `detail.html`, `edit.html`, and partials for the scoring breakdown
  (`data.html`, `detail_table.html`, `points.html`, `score.html`, `step.html`,
  `split_horizontal.html`, `split_vertical.html`).
- `tests/` — Test modules: `test_interval.py` (the `Interval` class),
  `test_models.py` (model behavior and scoring), `test_validators.py`
  (model and view validators), and `test_views.py` (view behavior, including
  publish and edit-lock rules).
- `validators/` — Validation logic shared between models and views:
  `common.py` for shared helpers, `models/curation.py` and `models/evidence.py`
  for model-level `clean()` validators, and `views.py` for the view-level
  validators called from `EvidenceEdit.form_valid`.
