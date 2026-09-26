# `publication`

This Django app manages publications used as evidence sources in HLA curations. Every publication is a PubMed article. Migration `0004_delete_preprint_publications` deleted the old bioRxiv and medRxiv preprints (stopping with an error if any evidence cited one), and migration `0005_remove_publication_type_and_doi` removed the `publication_type` and `doi` fields. It handles creation, display, and history tracking of publication records, automatically fetching metadata such as title, author, and year from PubMed when a new publication is added.

### `__init__.py`

Empty file that marks `publication` as a Python package.

### `admin.py`

Registers the `Publication` model with the Django admin site using `SimpleHistoryAdmin`, enabling browsable change history alongside standard list filtering and search by title, author, and PubMed ID.

### `apps.py`

Defines the `PublicationConfig` app configuration class, setting the app name and the default primary key field type.

### `clients.py`

Contains functions for fetching publication metadata from the NCBI PubMed E-utilities API (via XML). Provides helpers to extract title, primary author, and publication year from the response.

### `fixtures/test_publications.json`

Django fixture containing a sample PubMed `Publication` record used to seed the database during tests.

### `forms.py`

Defines `PublicationForm`, a `ModelForm` for creating a PubMed `Publication` that exposes only the `pubmed_id` field, with help text warning curators not to enter PubMed IDs of preprints.

### `models.py`

Defines the `Publication` model with fields for slug, a required and unique PubMed ID, title, author, publication year, and audit timestamps. The slug is auto-generated as `P<pk:06d>` on first save, and `django-simple-history` tracks all changes.

### `tables.py`

Defines `PublicationTable` using `django-tables2` to render the publication list, with the slug as a link to the detail page and the title rendered in italics.

### `templates/publication/change.html`

Displays the details of a single historical change to a publication, rendered within a breadcrumb trail from Home through Publication Search and publication detail to the specific change event.

### `templates/publication/create.html`

Renders the form for adding a new publication, which has a single PubMed ID input.

### `templates/publication/detail.html`

Displays all fields for a single publication in a table, with an external link to PubMed, and a collapsible section listing any evidence records associated with the publication.

### `templates/publication/history.html`

Renders the full change history for a publication by including the shared `common/history/history_body.html` partial, with breadcrumb navigation back to the publication detail page.

### `templates/publication/list.html`

Renders the publication search/list page, including a search input, a `django-tables2` results table, and a button to navigate to the create publication form.

### `tests/__init__.py`

Empty file that marks `tests` as a Python package.

### `tests/test_clients.py`

Contract tests that make real HTTP calls to the PubMed API to verify that the client functions correctly fetch and parse title, author, and year. These tests are skipped by default and only run when the `RUN_CONTRACT_TESTS=1` environment variable is set.

### `tests/test_migrations.py`

Tests for the `0004_delete_preprint_publications` data migration, run against the migration state before it, covering the deletion of preprint publications and the error raised when evidence cites a preprint.

### `tests/test_models.py`

Unit tests for the `Publication` model, covering the required PubMed ID and the string representation.

### `tests/test_views.py`

Integration tests for the publication views covering creation of PubMed publications (with mocked API responses), the absence of preprint inputs, rejection of missing PubMed IDs and preprint submissions, and basic rendering checks for the detail and list views.

### `urls.py`

Maps URL patterns to publication views: `create`, `<slug>/detail`, `<slug>/history`, `<slug>/history/<history_id>/change`, and `list`.

### `views.py`

Implements the five publication views: `PublicationCreate` fetches metadata from PubMed and saves the record; `PublicationDetail` shows a single publication; `PublicationHistory` and `PublicationChange` display the audit trail; and `PublicationList` provides a searchable, paginated table of all publications.
