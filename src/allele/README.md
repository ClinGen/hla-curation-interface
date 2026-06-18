# `allele`

The `allele` app manages HLA alleles within the HCI. It provides a model for storing
allele names and their associated ClinGen Allele Registry (CAR) IDs, a client for
fetching allele data from the CAR API at creation time, and views for listing, creating,
and inspecting alleles. Change history is tracked on every allele record via
`django-simple-history`.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers the `Allele` model with the Django admin site using `SimpleHistoryAdmin`,
exposing `name`, `car_id`, `added_by`, and `added_at` in the list view and making
`added_by` and `added_at` read-only.

### `apps.py`

Defines the `AlleleConfig` app configuration, setting the app name to `allele` and the
default primary-key field type to `BigAutoField`.

### `clients.py`

Contains functions for interacting with the ClinGen Allele Registry (CAR) API.
`fetch_allele_data` makes an HTTP GET request to the CAR HLA description endpoint for a
given allele name and returns the parsed JSON response (or `None` on any error), and
`get_car_id` extracts the CAR ID string from that response.

### `fixtures/test_alleles.json`

A Django fixture containing three sample `Allele` records (slugs `A000001`–`A000003`)
used to seed the database during automated tests.

### `forms.py`

Defines `AlleleForm`, a `ModelForm` for the `Allele` model that exposes only the `name`
field for user input.

### `models.py`

Defines the `Allele` model with fields for a human-readable slug (auto-generated as
`A000001`, etc.), allele name, CAR ID, the user who added the record, and timestamps.
History tracking is added via `HistoricalRecords`, and `get_absolute_url` resolves to
the allele detail view.

### `templates/allele/change.html`

Renders a detail page for a single history change record on an allele, displaying a
breadcrumb trail from Home through Allele Search and the allele's detail and history
pages, then including the shared `common/history/change_body.html` partial.

### `templates/allele/create.html`

Renders a form page for adding a new allele to the HCI, with a breadcrumb back to Home
and a POST form containing the allele name text input and a Submit button.

### `templates/allele/detail.html`

Renders a detail page for a single allele, displaying its HCI Allele ID, name, ClinGen
Allele Registry ID (as a linkout when present), and timestamps. It also includes
collapsible sections for associated curations and haplotypes when they exist.

### `templates/allele/history.html`

Renders a history page for a single allele, displaying a breadcrumb trail back through
Allele Search and the allele's detail page, then including the shared
`common/history/history_body.html` partial with the allele's change records.

### `templates/allele/list.html`

Renders the Allele Search page, showing the `allele/partials/table.html` partial with
all alleles and a link to the Add Allele page.

### `templates/allele/partials/table.html`

Renders a DataTables-powered HTML table of alleles with columns for ID (linked to the
detail page), Name, CAR ID (as a linkout when present), and Updated date.

### `tests.py`

Contains Django `TestCase` classes for the allele create, detail, and list views,
exercising form validation, CAR API integration (via mocking), access control via
`ProtectedViewTestMixin`, and correct template rendering.

### `urls.py`

Maps URL patterns for the allele app: `create`, `<slug>/detail`, `<slug>/history`,
`<slug>/history/<history_id>/change`, and `list`, each wired to the corresponding
class-based view.

### `views.py`

Defines five class-based views — `AlleleCreate`, `AlleleDetail`, `AlleleHistory`,
`AlleleChange`, and `AlleleList` — all protected by `ProtectedViewMixin`. `AlleleCreate`
fetches CAR data on form submission and stores the CAR ID; `AlleleHistory` and
`AlleleChange` populate context with history records and field-level diffs via
`resolve_changes`.
