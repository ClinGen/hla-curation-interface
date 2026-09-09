# `allele`

This Django app manages HLA alleles within the HLA Curation Interface. It handles creating and viewing alleles, looking up their ClinGen Allele Registry (CAR) IDs, and tracking the full change history of each record. The app exposes list, detail, create, history, and change-diff views, all protected behind authentication and permissions.

### `__init__.py`

Empty file that marks the directory as a Python package.

### `admin.py`

Registers the `Allele` model with Django's admin site using `SimpleHistoryAdmin`, exposing name, CAR ID, added-by, and added-at in the list view with CAR ID search and read-only audit fields.

### `apps.py`

Defines the `AlleleConfig` app configuration, setting the app name to `allele` and using `BigAutoField` as the default primary key type.

### `clients.py`

Contains functions for interacting with the ClinGen Allele Registry (CAR) API. `fetch_allele_data` queries the CAR endpoint by allele name and returns the JSON response, while `get_car_id` extracts the registry ID from that response.

### `fixtures/test_alleles.json`

Provides three sample `Allele` records (e.g., `A*01:02:03`, `B*04:05:06`, `C*07:08:09`) used as test fixtures in unit tests.

### `forms.py`

Defines `AlleleForm`, a `ModelForm` for the `Allele` model that exposes only the `name` field for user input.

### `models.py`

Defines the `Allele` model with fields for a human-readable slug ID, allele name, CAR ID, and audit timestamps. The `save` method auto-generates the slug in the format `A000001`, and `HistoricalRecords` from `django-simple-history` tracks all changes.

### `tables.py`

Defines `AlleleTable` using `django-tables2` for rendering paginated allele lists. The slug column links to the detail view, and the CAR ID column renders as an external link to the ClinGen Allele Registry when a value is present.

### `templates/allele/change.html`

Displays a single historical change to an allele, including breadcrumb navigation back through the list, detail, and history views. Uses the shared `common/history/change_body.html` partial to render the diff.

### `templates/allele/create.html`

Renders the form for adding a new allele, with breadcrumb navigation and a single name input field that submits via POST.

### `templates/allele/detail.html`

Shows all fields for a single allele (slug, name, CAR ID, added and updated dates) in a table, with a link to the history view and collapsible sections for associated curations and haplotypes.

### `templates/allele/history.html`

Lists the full change history for an allele with breadcrumb navigation, delegating the history table rendering to the shared `common/history/history_body.html` partial.

### `templates/allele/list.html`

Renders the allele search page with a search input, a paginated results table, and an "Add Allele" button linking to the create view.

### `tests.py`

Contains tests for the allele create, detail, and list views. Covers access protection (via `ProtectedViewTestMixin`), form validation, CAR API integration on creation (using mocks), and correct rendering of related haplotypes and fixture data.

### `urls.py`

Maps URL patterns for the five allele views: `allele-create`, `allele-detail`, `allele-history`, `allele-change`, and `allele-list`.

### `views.py`

Implements the five class-based views for alleles, all protected by `ProtectedViewMixin`. `AlleleCreate` fetches the CAR ID on form submission; `AlleleDetail` injects related curation and haplotype tables into context; `AlleleHistory` builds a history table; `AlleleChange` resolves the field-level diff for a single history record; and `AlleleList` provides paginated, searchable results.
