# Publication

This directory contains the `publication` Django app for the HLA Curation
Interface (HCI). The app stores the publications that curations cite. Each
`Publication` is one of three types — a PubMed article, a bioRxiv preprint, or
a medRxiv preprint — identified by either a PubMed ID (for PubMed articles) or
a DOI (for the rxiv preprints). When a curator submits a new publication, the
app fetches the corresponding metadata from PubMed's E-utilities API or the
bioRxiv/medRxiv API and persists the title, primary author surname, and
publication year alongside the identifier.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers the `Publication` model with Django's admin site and
  configures its list display, list filter, search fields, and read-only
  fields (`added_by`, `added_at`).
- `apps.py` — Django `AppConfig` for the `publication` app.
- `clients.py` — Houses code that interacts with third-party services:
  `fetch_pubmed_data` retrieves a PubMed article by ID and `get_pubmed_title`,
  `get_pubmed_author`, and `get_pubmed_year` extract fields from the PubMed
  XML response; `fetch_rxiv_data` retrieves a bioRxiv or medRxiv paper by DOI
  and `get_rxiv_title`, `get_rxiv_author`, and `get_rxiv_year` extract fields
  from the rxiv JSON response.
- `forms.py` — Defines `PublicationForm`, a `ModelForm` exposing
  `publication_type` (rendered as a radio select), `doi`, and `pubmed_id`; the
  title, author, and year are populated from the upstream API in the view.
- `models.py` — Defines the `Publication` model with `slug` (a `P######`
  human-readable ID generated on save), `publication_type`, `pubmed_id`, `doi`,
  `title`, `author`, `publication_year`, `added_by`, and `added_at`. Its
  `clean` method calls the validators in `validators/models.py`, and
  `get_absolute_url` points at the `publication-detail` view.
- `urls.py` — URL routes for the app: `publication-create`,
  `publication-detail`, and `publication-list`.
- `views.py` — Class-based views for the app: `PublicationCreate` (overrides
  `form_valid` to fetch PubMed or rxiv data, populate
  `title`/`author`/`publication_year`/`added_by`, and warn the user if the
  upstream call fails), `PublicationDetail`, and `PublicationList`. All views
  inherit from `ProtectedViewMixin`.

## Subdirectories

- `constants/` — Enum-style constants used by the model: `models.py` defines
  `PublicationTypes` (`PUBMED`, `BIORXIV`, `MEDRXIV`) and the matching
  `PUBLICATION_TYPE_CHOICES` mapping.
- `fixtures/` — JSON fixtures: `test_publications.json` provides the test data
  loaded by `PublicationDetailTest` and `PublicationListTest`.
- `migrations/` — Django database migrations for the `Publication` model.
- `templates/publication/` — HTML templates for the app: `create.html`
  (with client-side JavaScript that toggles the `pubmed_id` and `doi` inputs
  based on the selected publication type), `detail.html`, `list.html`, and a
  `partials/rxiv_warning.html` partial that warns curators preprints cannot be
  included in published curations.
- `tests/` — Tests for the app: `test_views.py` covers the create, detail, and
  list views with the upstream API calls patched out, and `test_clients.py`
  contains contract tests that hit the real PubMed, bioRxiv, and medRxiv APIs
  (skipped by default; run with `RUN_CONTRACT_TESTS=1`).
- `validators/` — Validation logic for the model: `models.py` defines
  `validate_publication_type_pubmed` (requires a PubMed ID for PubMed
  articles), `validate_publication_type_biorxiv` (requires a DOI for bioRxiv
  papers), and `validate_publication_type_medrxiv` (requires a DOI for
  medRxiv papers).
