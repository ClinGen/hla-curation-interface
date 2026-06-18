# `publication`

Django app that manages scientific publications — PubMed articles, bioRxiv preprints,
and medRxiv preprints — referenced by HLA curations. It provides a `Publication` model,
clients that fetch metadata from the PubMed E-utilities API and the bioRxiv/medRxiv API,
and the full set of views, forms, templates, and URL routes for creating, browsing, and
auditing publications within the HCI.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers the `Publication` model with the Django admin site using `SimpleHistoryAdmin`,
displaying `title`, `author`, `publication_type`, and `doi` in the list view with
filtering by type, search by title/author/DOI, and `added_by`/`added_at` as read-only
fields.

### `apps.py`

Defines the `PublicationConfig` app configuration, setting `BigAutoField` as the default
primary key type and registering the app under the name `publication`.

### `clients.py`

Contains functions for fetching and parsing publication metadata from external APIs:
`fetch_pubmed_data` and `get_pubmed_title`/`get_pubmed_author`/`get_pubmed_year` work
against the NCBI PubMed E-utilities XML endpoint, while `fetch_rxiv_data` and
`get_rxiv_title`/`get_rxiv_author`/`get_rxiv_year` work against the bioRxiv/medRxiv JSON
API, always extracting the most recent version from the collection.

### `constants/__init__.py`

Empty file; marks this directory as a Python package.

### `constants/models.py`

Defines the `PublicationTypes` class with three type codes (`PUBMED = "PUB"`,
`BIORXIV = "BIO"`, `MEDRXIV = "MED"`) and the corresponding `PUBLICATION_TYPE_CHOICES`
dict used by the `Publication` model field.

### `fixtures/test_publications.json`

Django fixture providing three sample `publication.publication` records (slugs
`P000001`–`P000003`, covering PubMed, bioRxiv, and medRxiv types) used by the test suite
to pre-populate the database without hitting external APIs.

### `forms.py`

Defines `PublicationForm`, a `ModelForm` for `Publication` that exposes
`publication_type` (rendered as radio buttons), `doi`, and `pubmed_id` fields.

### `models.py`

Defines the `Publication` model with fields for slug, publication type, PubMed ID, DOI,
title, primary author surname, publication year, and audit metadata. The `save` method
auto-generates a zero-padded slug (`P000001` style), `clean` delegates to the three
model validators, and historical change tracking is provided via `simple_history`.

### `templates/publication/change.html`

Displays a single historical change record for a publication, with a breadcrumb trail
back through the publication list, detail, and history pages, and the change body
rendered via the shared `common/history/change_body.html` partial.

### `templates/publication/create.html`

Renders the "Add Publication" form with radio buttons for publication type, a
conditional PubMed ID text input (hidden for preprint types), a DOI text input (hidden
for PubMed type) with the preprint warning partial, and JavaScript that toggles field
visibility based on the selected type.

### `templates/publication/detail.html`

Shows the detail view for a single publication, displaying its HCI ID, title, primary
author, publication year, PubMed ID (linked to PubMed), DOI (linked via doi.org), and
timestamps. If any evidence items reference the publication, they are listed in a
collapsible table showing curation and classification details.

### `templates/publication/history.html`

Shows the full edit history for a publication using the shared
`common/history/history_body.html` partial, with breadcrumbs to the list and detail
pages.

### `templates/publication/list.html`

Renders a searchable DataTables table of all publications with columns for HCI ID,
title, author, year, PMID, DOI, and last-updated date, plus an "Add Publication" button.

### `templates/publication/partials/rxiv_warning.html`

A Bulma warning message component that informs curators that preprint publications may
be used in curations but cannot be included in published curations.

### `tests/__init__.py`

Empty file; marks this directory as a Python package.

### `tests/test_clients.py`

Contains opt-in contract tests (skipped by default unless `RUN_CONTRACT_TESTS=1` is set)
that make live API calls to PubMed, bioRxiv, and medRxiv to verify that the client
functions correctly fetch and extract title, author, and year from real records.

### `tests/test_views.py`

Contains `TestCase` classes for `PublicationCreate`, `PublicationDetail`, and
`PublicationList` views, verifying page content, access control via
`ProtectedViewTestMixin`, form validation, and that successful POSTs for each
publication type create records populated with data from mocked API clients.

### `urls.py`

Maps the five publication URL patterns — `create`, `<slug>/detail`, `<slug>/history`,
`<slug>/history/<id>/change`, and `list` — to their corresponding view classes.

### `validators/__init__.py`

Empty file; marks this directory as a Python package.

### `validators/models.py`

Provides three validation functions called from `Publication.clean`:
`validate_publication_type_pubmed` requires a PubMed ID for PubMed publications,
`validate_publication_type_biorxiv` requires a DOI for bioRxiv papers, and
`validate_publication_type_medrxiv` requires a DOI for medRxiv papers, each raising
`ValidationError` when the required field is absent.

### `views.py`

Implements five class-based views — `PublicationCreate`, `PublicationDetail`,
`PublicationHistory`, `PublicationChange`, and `PublicationList` — all protected by
`ProtectedViewMixin`. `PublicationCreate.form_valid` branches on publication type to
call either the PubMed or Rxiv client, populating `author`, `title`, `publication_year`,
and `added_by` before saving. `PublicationChange` uses `resolve_changes` to build a diff
for the selected history record.
