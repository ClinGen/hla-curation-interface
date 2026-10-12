# `publication`

This Django app manages publications used as evidence sources in HLA curations. Every publication is a PubMed article. Migration `0004_delete_preprint_publications` deleted the old bioRxiv and medRxiv preprints (stopping with an error if any evidence cited one), and migration `0005_remove_publication_type_and_doi` removed the `publication_type` and `doi` fields. It handles creation, display, and history tracking of publication records, automatically fetching metadata such as title, authors, and year from PubMed when a new publication is added.

### `__init__.py`

Empty file that marks `publication` as a Python package.

### `admin.py`

Registers the `Publication` model with the Django admin site using `SimpleHistoryAdmin`, enabling browsable change history alongside standard list filtering and search by title, author, and PubMed ID.

### `apps.py`

Defines the `PublicationConfig` app configuration class, setting the app name and the default primary key field type.

### `clients.py`

Contains functions for fetching publication metadata from the NCBI PubMed E-utilities API (via XML). Provides helpers to extract the title, publication year, primary author (`get_pubmed_author`, the surname of the first person in the article's author list), and every author in order (`get_pubmed_authors`, each as "LastName Initials", or the group name for group authors). `refresh_from_pubmed` sets a publication's title, primary author, authors, and year from PubMed without saving, and returns `False`, leaving the publication unchanged, when the fetch fails. Adding a publication and the Refresh from PubMed button both use it.

### `fixtures/test_publications.json`

Django fixture containing a sample PubMed `Publication` record used to seed the database during tests. Its authors include a non-primary author, Juniper, for author search tests.

### `forms.py`

Defines `PublicationForm`, a `ModelForm` for creating a PubMed `Publication` that exposes only the `pubmed_id` field, with help text warning curators not to enter PubMed IDs of preprints.

### `models.py`

Defines the `Publication` model with fields for slug, a required and unique PubMed ID, title, author (the primary author's surname), authors (every author in PubMed order, joined with "; "), publication year, and audit timestamps. The slug is auto-generated as `P<pk:06d>` on first save, and `django-simple-history` tracks all changes.

### `tables.py`

Defines `PublicationTable` using `django-tables2` to render the publication list, with the slug as a link to the detail page and the title rendered in italics.

### `templates/publication/change.html`

Displays the details of a single historical change to a publication, rendered within a breadcrumb trail from Home through Publication Search and publication detail to the specific change event.

### `templates/publication/create.html`

Renders the form for adding a new publication, which has a single PubMed ID input.

### `templates/publication/detail.html`

Displays all fields for a single publication in a table, including the full author list (or "------" when it's empty), with an external link to PubMed, View History and Refresh from PubMed buttons (the latter posts to `publication-refresh` after a confirmation modal), and a collapsible section listing any evidence records associated with the publication.

### `templates/publication/history.html`

Renders the full change history for a publication by including the shared `common/history/history_body.html` partial, with breadcrumb navigation back to the publication detail page.

### `templates/publication/list.html`

Renders the publication search/list page, including a search input, a `django-tables2` results table, and a button to navigate to the create publication form.

### `tests/__init__.py`

Empty file that marks `tests` as a Python package.

### `tests/test_clients.py`

Contract tests that make real HTTP calls to the PubMed API to verify that the client functions correctly fetch and parse title, primary author, all authors, and year. These tests are skipped by default and only run when the `RUN_CONTRACT_TESTS=1` environment variable is set.

### `tests/test_clients_unit.py`

Offline unit tests for the PubMed author parsers, using inline XML: author order, group authors, a missing author list, and a `LastName` outside the author list, which the parsers ignore.

### `tests/test_migrations.py`

Tests for the `0004_delete_preprint_publications` data migration, run against the migration state before it, covering the deletion of preprint publications and the error raised when evidence cites a preprint.

### `tests/test_models.py`

Unit tests for the `Publication` model, covering the required PubMed ID and the string representation.

### `tests/test_views.py`

Integration tests for the publication views covering creation of PubMed publications (with mocked API responses), the absence of preprint inputs, rejection of missing PubMed IDs and preprint submissions, basic rendering checks for the detail and list views, the detail page's author list and its "------" placeholder, publication search matching a non-primary author, and `refresh_from_pubmed` and the refresh view (success, PubMed failure, GET, permissions, and the detail page's button).

### `urls.py`

Maps URL patterns to publication views: `create`, `<slug>/detail`, `<slug>/refresh`, `<slug>/history`, `<slug>/history/<history_id>/change`, and `list`.

### `views.py`

Implements the six publication views: `PublicationCreate` fetches the title, primary author, full author list, and year from PubMed and saves the record; `publication_refresh` (POST only, for curators) updates an existing publication from PubMed, or shows `REFRESH_FAILED_MESSAGE` and changes nothing if PubMed fails; `PublicationDetail` shows a single publication; `PublicationList` searches by ID, title, primary author, any author, and PubMed ID; `PublicationHistory` and `PublicationChange` display the audit trail; and `PublicationList` provides a searchable, paginated table of all publications.
