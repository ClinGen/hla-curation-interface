# `disease`

Django app that manages Mondo Disease Ontology entries used in HLA curations. It
provides a `Disease` model backed by the Mondo ontology, a client that fetches disease
names and IRIs from the EBI Ontology Lookup Service (OLS), and the full set of views,
forms, templates, and URL routes for creating, browsing, and auditing diseases within
the HCI.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers the `Disease` model with the Django admin site using `SimpleHistoryAdmin`,
exposing list display, filtering by `disease_type`, and search by name and Mondo ID,
with `added_by` and `added_at` as read-only fields.

### `apps.py`

Defines the `DiseasesConfig` app configuration, setting `BigAutoField` as the default
primary key type and registering the app under the name `disease`.

### `clients.py`

Contains functions that interact with the EBI Ontology Lookup Service:
`fetch_disease_data` retrieves the raw JSON for a given Mondo ID, and `get_name` and
`get_iri` extract the disease label and IRI from that response, returning empty strings
and logging warnings on failure.

### `constants/__init__.py`

Empty file; marks this directory as a Python package.

### `constants/models.py`

Defines the `DiseaseTypes` class with the single supported type code `MONDO = "MON"` and
the corresponding `DISEASE_TYPE_CHOICES` dict used by the `Disease` model field.

### `fixtures/test_diseases.json`

Django fixture providing three sample `disease.disease` records (slugs
`D000001`–`D000003`) used by the test suite to pre-populate the database without hitting
external APIs.

### `forms.py`

Defines `DiseaseForm`, a `ModelForm` for the `Disease` model that exposes only the
`mondo_id` field, which the user supplies when adding a new disease.

### `models.py`

Defines the `Disease` model with fields for slug, disease type, Mondo ID, IRI, name, and
audit metadata (`added_by`, `added_at`, `updated_at`). The `save` method auto-generates
a zero-padded slug (`D000001` style), and `clean` delegates to the model validators.
Historical change tracking is provided via `simple_history`.

### `templates/disease/change.html`

Displays a single historical change record for a disease, with a breadcrumb trail back
through the disease list, detail, and history pages, and the change body rendered via
the shared `common/history/change_body.html` partial.

### `templates/disease/create.html`

Renders the "Add Disease" form, showing a Mondo ID text input with a link to the EBI OLS
search for Mondo and a submit button.

### `templates/disease/detail.html`

Shows the detail view for a single disease, displaying its HCI ID, Mondo ID (linked to
its IRI), and timestamps. If any curations reference the disease, they are listed in a
collapsible section.

### `templates/disease/history.html`

Shows the full edit history for a disease using the shared
`common/history/history_body.html` partial, with breadcrumbs to the list and detail
pages.

### `templates/disease/list.html`

Renders a searchable DataTables table of all diseases with columns for HCI ID, name,
Mondo ID (external link), and last-updated date, plus an "Add Disease" button.

### `tests.py`

Contains `TestCase` classes for `DiseaseCreate`, `DiseaseDetail`, and `DiseaseList`
views, verifying page content, access control via `ProtectedViewTestMixin`, form
validation, and that a successful POST creates a disease with data fetched from a mocked
OLS client.

### `urls.py`

Maps the five disease URL patterns — `create`, `<slug>/detail`, `<slug>/history`,
`<slug>/history/<id>/change`, and `list` — to their corresponding view classes.

### `validators/__init__.py`

Empty file; marks this directory as a Python package.

### `validators/models.py`

Provides two validation functions called from `Disease.clean`:
`validate_disease_type_mondo` raises a `ValidationError` if a Mondo disease has no Mondo
ID, and `validate_mondo_id` raises a `ValidationError` if the Mondo ID does not start
with the `MONDO:` prefix.

### `views.py`

Implements five class-based views — `DiseaseCreate`, `DiseaseDetail`, `DiseaseHistory`,
`DiseaseChange`, and `DiseaseList` — all protected by `ProtectedViewMixin`.
`DiseaseCreate.form_valid` calls the OLS client to populate the `name` and `iri` fields
before saving, and `DiseaseChange` uses `resolve_changes` to build a diff for the
selected history record.
