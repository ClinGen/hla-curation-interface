# Disease

This directory contains the `disease` Django app for the HLA Curation Interface
(HCI). The app stores the diseases that curations are paired with. Each
`Disease` is identified by a Mondo Disease Ontology ID; when a curator submits
a new Mondo ID, the app fetches the corresponding term from the EBI Ontology
Lookup Service (OLS) and persists the disease's name and IRI alongside the ID.
Only Mondo-typed diseases are supported for now, but the model leaves room for
additional ontologies.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers the `Disease` model with Django's admin site and
  configures its list display, list filter, search fields, and read-only
  fields (`added_by`, `added_at`).
- `apps.py` — Django `AppConfig` for the `disease` app.
- `clients.py` — Houses code that interacts with the EBI Ontology Lookup
  Service: `fetch_disease_data` retrieves a Mondo term by ID, and `get_name`
  and `get_iri` extract the disease's label and IRI from the OLS response.
- `forms.py` — Defines `DiseaseForm`, a `ModelForm` exposing only the
  `mondo_id` field; the name and IRI are populated from OLS in the view.
- `models.py` — Defines the `Disease` model with `slug` (a `D######`
  human-readable ID generated on save), `disease_type`, `mondo_id`, `iri`,
  `name`, `added_by`, and `added_at`. Its `clean` method calls the validators
  in `validators/models.py`, and `get_absolute_url` points at the
  `disease-detail` view.
- `tests.py` — Tests for the create, detail, and list views, including a
  patched `fetch_disease_data` to verify that valid form submissions persist
  the disease and copy the OLS-supplied name and IRI onto the record.
- `urls.py` — URL routes for the app: `disease-create`, `disease-detail`, and
  `disease-list`.
- `views.py` — Class-based views for the app: `DiseaseCreate` (overrides
  `form_valid` to fetch OLS data, populate `name`/`iri`/`added_by`, and warn
  the user if the OLS call fails), `DiseaseDetail`, and `DiseaseList`. All
  views inherit from `ProtectedViewMixin`.

## Subdirectories

- `constants/` — Enum-style constants used by the model: `models.py` defines
  `DiseaseTypes` (currently just `MONDO`) and the matching
  `DISEASE_TYPE_CHOICES` mapping.
- `fixtures/` — JSON fixtures: `test_diseases.json` provides the test data
  loaded by `DiseaseDetailTest` and `DiseaseListTest`.
- `migrations/` — Django database migrations for the `Disease` model.
- `templates/disease/` — HTML templates for the app: `create.html`,
  `detail.html`, and `list.html`.
- `validators/` — Validation logic for the model: `models.py` defines
  `validate_disease_type_mondo` (requires a Mondo ID when the disease type is
  Mondo) and `validate_mondo_id` (requires the `MONDO:` prefix).
