# `disease`

This Django app manages disease records used in HLA curation, backed by the Mondo Disease Ontology. It provides the `Disease` model along with the views, forms, templates, and supporting utilities needed to create, browse, and audit disease entries. Disease data (names and IRIs) is fetched automatically from the EBI Ontology Lookup Service (OLS) when a new disease is added.

### `__init__.py`

Empty file that marks `disease` as a Python package.

### `admin.py`

Registers the `Disease` model with the Django admin site using `SimpleHistoryAdmin`, enabling history tracking and exposing search, filter, and display options for `name`, `mondo_id`, and `disease_type`.

### `apps.py`

Defines the `DiseasesConfig` app configuration class, setting the app name to `disease` and specifying `BigAutoField` as the default primary key type.

### `clients.py`

Contains functions for interacting with the EBI Ontology Lookup Service (OLS). `fetch_disease_data` retrieves raw JSON for a given Mondo ID, while `get_name` and `get_iri` extract the disease label and IRI from that response.

### `constants/__init__.py`

Empty file that makes `constants` a Python package.

### `constants/models.py`

Defines the `DiseaseTypes` class (currently with a single `MONDO` type) and the `DISEASE_TYPE_CHOICES` mapping used by the `Disease` model's `disease_type` field.

### `fixtures/test_diseases.json`

Django fixture containing three sample `Disease` records (Mondo type) used to seed the database during tests.

### `forms.py`

Defines `DiseaseForm`, a `ModelForm` for the `Disease` model that exposes only the `mondo_id` field, which is the sole input required from users when adding a disease.

### `models.py`

Defines the `Disease` model with fields for `slug`, `disease_type`, `mondo_id`, `iri`, `name`, `added_by`, `added_at`, and `updated_at`. It auto-generates a human-readable slug on first save, tracks history via `simple_history`, and runs model-level validation via `clean`.

### `tables.py`

Defines `DiseaseTable` using `django-tables2`, rendering columns for ID (linked to the detail page), name, Mondo ID (linked externally to OLS), and last-updated date.

### `templates/disease/change.html`

Displays the details of a single historical change to a disease record, with breadcrumb navigation back to the disease's detail and history pages.

### `templates/disease/create.html`

Renders the form for adding a new disease, accepting a Mondo ID and including a link to the EBI OLS for looking up valid IDs.

### `templates/disease/detail.html`

Shows a disease record's fields (HCI ID, Mondo ID, added date, updated date) and lists any associated curations in a table.

### `templates/disease/history.html`

Displays the full audit history of a disease record using a shared history table partial, with breadcrumb navigation to the detail page.

### `templates/disease/list.html`

Renders the disease search page, including a search input, a paginated results table, and a button to add a new disease.

### `tests.py`

Contains test cases for `DiseaseCreate`, `DiseaseDetail`, and `DiseaseList` views, verifying authentication requirements, correct template rendering, and that valid/invalid form submissions behave as expected (including mocking the OLS API call).

### `urls.py`

Maps URL patterns for the disease app: create, detail, history, change, and list endpoints, all prefixed by the project-level URL configuration.

### `validators/__init__.py`

Empty file that makes `validators` a Python package.

### `validators/models.py`

Provides two model-level validator functions: `validate_disease_type_mondo` ensures a Mondo ID is present when the disease type is Mondo, and `validate_mondo_id` enforces that the ID starts with the `MONDO:` prefix.

### `views.py`

Implements the five class-based views for the disease app: `DiseaseCreate` (fetches OLS data on form submission), `DiseaseDetail` (includes associated curations), `DiseaseHistory` (renders a history table), `DiseaseChange` (shows field-level diffs for a single historical record), and `DiseaseList` (searchable, paginated list).
