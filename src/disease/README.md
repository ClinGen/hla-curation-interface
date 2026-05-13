# `disease`

This directory contains the `disease` Django app for the HLA Curation Interface
(HCI). The app stores the diseases that curations are paired with. Each
`Disease` is identified by a Mondo Disease Ontology ID; when a curator submits
a new Mondo ID, the app fetches the corresponding term from the EBI Ontology
Lookup Service (OLS) and persists the disease's name and IRI alongside the ID.
Only Mondo-typed diseases are supported for now, but the model leaves room for
additional ontologies.

### `__init__.py`

Marks the directory as a Python package.

### `admin.py`

Registers the `Disease` model with Django's admin site and configures its list
display, list filter, search fields, and read-only fields (`added_by`,
`added_at`).

### `apps.py`

Django `AppConfig` for the `disease` app.

### `clients.py`

Houses code that interacts with the EBI Ontology Lookup Service:
`fetch_disease_data` retrieves a Mondo term by ID, and `get_name` and `get_iri`
extract the disease's label and IRI from the OLS response.

### `constants/__init__.py`

Marks the directory as a Python package.

### `constants/models.py`

Enum-style constants used by the `Disease` model: defines `DiseaseTypes`
(currently just `MONDO`) and the matching `DISEASE_TYPE_CHOICES` mapping.

### `fixtures/test_diseases.json`

Django fixture containing test `Disease` records used by `DiseaseDetailTest`
and `DiseaseListTest`.

### `forms.py`

Defines `DiseaseForm`, a `ModelForm` exposing only the `mondo_id` field; the
name and IRI are populated from OLS in the view.

### `models.py`

Defines the `Disease` model with `slug` (a `D######` human-readable ID
generated on save), `disease_type`, `mondo_id`, `iri`, `name`, `added_by`, and
`added_at`. Its `clean` method calls the validators in `validators/models.py`,
and `get_absolute_url` points at the `disease-detail` view.

### `templates/disease/create.html`

HTML template that renders the disease creation form for the `DiseaseCreate`
view.

### `templates/disease/detail.html`

HTML template that renders the disease detail page for the `DiseaseDetail`
view.

### `templates/disease/list.html`

HTML template that renders the disease list for the `DiseaseList` view.

### `tests.py`

Tests for the create, detail, and list views, including a patched
`fetch_disease_data` to verify that valid form submissions persist the disease
and copy the OLS-supplied name and IRI onto the record.

### `urls.py`

URL routes for the app: `disease-create`, `disease-detail`, and `disease-list`.

### `validators/__init__.py`

Marks the directory as a Python package.

### `validators/models.py`

Model-level `clean()` validators for the `Disease` model:
`validate_disease_type_mondo` (requires a Mondo ID when the disease type is
Mondo) and `validate_mondo_id` (requires the `MONDO:` prefix).

### `views.py`

Class-based views for the app: `DiseaseCreate` (overrides `form_valid` to
fetch OLS data, populate `name`/`iri`/`added_by`, and warn the user if the OLS
call fails), `DiseaseDetail`, and `DiseaseList`. All views inherit from
`ProtectedViewMixin`.
