# `publication`

This Django app manages publications (PubMed articles, bioRxiv papers, and medRxiv papers) used as evidence sources in HLA curations. It handles creation, display, and history tracking of publication records, automatically fetching metadata such as title, author, and year from external APIs when a new publication is added.

### `__init__.py`

Empty file that marks `publication` as a Python package.

### `admin.py`

Registers the `Publication` model with the Django admin site using `SimpleHistoryAdmin`, enabling browsable change history alongside standard list filtering and search by title, author, and DOI.

### `apps.py`

Defines the `PublicationConfig` app configuration class, setting the app name and the default primary key field type.

### `clients.py`

Contains functions for fetching publication metadata from external APIs: the NCBI PubMed E-utilities API (via XML) and the bioRxiv/medRxiv API (via JSON). Provides helpers to extract title, primary author, and publication year from each API's response format.

### `constants/__init__.py`

Empty file that marks `constants` as a Python package.

### `constants/models.py`

Defines the `PublicationTypes` class with short codes (`PUB`, `BIO`, `MED`) for each supported publication source, and the `PUBLICATION_TYPE_CHOICES` dict used to populate the model field's choices.

### `fixtures/test_publications.json`

Django fixture containing three sample `Publication` records (one PubMed, one bioRxiv, one medRxiv) used to seed the database during tests.

### `forms.py`

Defines `PublicationForm`, a `ModelForm` for creating a `Publication` that exposes the `publication_type`, `doi`, and `pubmed_id` fields, rendering `publication_type` as a radio button group.

### `models.py`

Defines the `Publication` model with fields for slug, type, PubMed ID, DOI, title, author, publication year, and audit timestamps. The slug is auto-generated as `P<pk:06d>` on first save, and `django-simple-history` tracks all changes.

### `tables.py`

Defines `PublicationTable` using `django-tables2` to render the publication list, with the slug as a link to the detail page and the title rendered in italics.

### `templates/publication/change.html`

Displays the details of a single historical change to a publication, rendered within a breadcrumb trail from Home through Publication Search and publication detail to the specific change event.

### `templates/publication/create.html`

Renders the form for adding a new publication, with JavaScript that shows or hides the PubMed ID and DOI input fields based on the selected publication type radio button.

### `templates/publication/detail.html`

Displays all fields for a single publication in a table, with external links to PubMed and doi.org, and a collapsible section listing any evidence records associated with the publication.

### `templates/publication/history.html`

Renders the full change history for a publication by including the shared `common/history/history_body.html` partial, with breadcrumb navigation back to the publication detail page.

### `templates/publication/list.html`

Renders the publication search/list page, including a search input, a `django-tables2` results table, and a button to navigate to the create publication form.

### `templates/publication/partials/rxiv_warning.html`

A small Bulma warning message box informing users that preprint publications (bioRxiv/medRxiv) cannot be included in published curations.

### `tests/__init__.py`

Empty file that marks `tests` as a Python package.

### `tests/test_clients.py`

Contract tests that make real HTTP calls to the PubMed, bioRxiv, and medRxiv APIs to verify that the client functions correctly fetch and parse title, author, and year. These tests are skipped by default and only run when the `RUN_CONTRACT_TESTS=1` environment variable is set.

### `tests/test_views.py`

Integration tests for the publication views covering creation of PubMed, bioRxiv, and medRxiv publications (with mocked API responses), validation failure behavior, and basic rendering checks for the detail and list views.

### `urls.py`

Maps URL patterns to publication views: `create`, `<slug>/detail`, `<slug>/history`, `<slug>/history/<history_id>/change`, and `list`.

### `validators/__init__.py`

Empty file that marks `validators` as a Python package.

### `validators/models.py`

Contains model-level validation functions called from `Publication.clean()` that raise `ValidationError` if a required identifier is missing for a given publication type (PubMed ID for PubMed, DOI for bioRxiv or medRxiv).

### `views.py`

Implements the five publication views: `PublicationCreate` fetches metadata from external APIs and saves the record; `PublicationDetail` shows a single publication; `PublicationHistory` and `PublicationChange` display the audit trail; and `PublicationList` provides a searchable, paginated table of all publications.
