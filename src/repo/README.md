# Repo

This directory contains the `repo` Django app for the HLA Curation Interface
(HCI). The app is the public-facing repository of curations that have been
finalized and published. When a curator publishes a `Curation` whose status is
`DONE`, a `PublishedCuration` record is created that snapshots the publication
event (publisher, timestamp, version) and points back at the underlying
`Curation`. The app exposes a list view, a detail view, and JSON download
endpoints (single curation and bulk export) that serialize a published
curation along with its related allele or haplotype, disease, and evidence.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `apps.py` — Django `AppConfig` for the `repo` app.
- `models.py` — Defines the `PublishedCuration` model, a one-to-one wrapper
  around `curation.Curation` with `published_at` (auto-set), `published_by`
  (FK to `User`), and `version` fields. `get_absolute_url` points at the
  `repo-detail` view.
- `serializers.py` — Plain-function serializers used by the JSON download
  views: `serialize_published_curation` produces a dictionary containing the
  publication metadata, the curation's status, classification, score, the
  associated allele or haplotype, the disease, and the list of evidence;
  `serialize_evidence` produces a dictionary for a single `Evidence` record
  (publication, statistics, demographics, flags, score, etc.).
- `urls.py` — URL routes for the app: `repo-search` (list view at the app
  root), `repo-download-all` (bulk JSON export), `repo-detail`, and
  `repo-download-single`.
- `views.py` — Views for the app: `PublishedCurationList` (a `ListView`
  rendering `repo/list.html`), `PublishedCurationDetail` (a `DetailView` keyed
  by the underlying curation's slug), `download_all_json` (returns every
  published curation as a JSON attachment named
  `hla_curations_all_<date>.json`), and `download_single_json` (returns one
  published curation as `hla_curation_<slug>.json`).
- `tests.py` — Tests for the app: `PublishedCurationModelTest` (model
  creation, string representation, one-to-one constraint, reverse
  relationship, and `get_absolute_url`), `CurationPublishViewTest` (the
  publish action defined in the `curation` app, exercised here because it
  produces `PublishedCuration` rows), `RepoSearchViewTest`,
  `PublishedCurationDetailViewTest`, and `JSONDownloadViewTest`.

## Subdirectories

- `migrations/` — Django database migrations for the `PublishedCuration`
  model.
- `templates/repo/` — HTML templates for the app: `list.html` (the public
  repository search/listing page) and `detail.html` (the per-curation page,
  which links to the JSON download).
