# `allele`

This directory contains the `allele` Django app for the HLA Curation Interface
(HCI). The app is responsible for managing HLA alleles within the system,
including creating new allele records (with data fetched from the ClinGen
Allele Registry), viewing allele details, and listing alleles. Each allele
record stores the user-supplied name (e.g., `DRB3*03:01:01`), the corresponding
ClinGen Allele Registry (CAR) ID, a human-readable slug ID, and metadata about
who added it and when.

### `__init__.py`

Marks the directory as a Python package.

### `admin.py`

Registers the `Allele` model with Django's admin site and configures the list
display, search fields, and read-only fields (`added_by`, `added_at`).

### `apps.py`

Django `AppConfig` for the `allele` app.

### `clients.py`

Houses code that interacts with the ClinGen Allele Registry third-party
service: `fetch_allele_data` retrieves allele data from the CAR HTTP endpoint,
and `get_car_id` extracts the CAR ID from the response.

### `fixtures/test_alleles.json`

Test fixture loaded by `AlleleDetailTest` and `AlleleListTest`. Provides three
`Allele` rows (`A000001`, `A000002`, `A000003`) with stable names, CAR IDs,
and `added_at` timestamps for use in view tests.

### `forms.py`

Defines `AlleleForm`, a `ModelForm` exposing only the `name` field of the
`Allele` model for the create view; the CAR ID and `added_by` are populated
in the view after fetching CAR data.

### `models.py`

Defines the `Allele` Django model with fields for `slug`, `name`, `car_id`,
`added_by`, and `added_at`. The `save` method auto-generates a human-readable
slug ID of the form `A######` after the first save, and `get_absolute_url`
points at the `allele-detail` view.

### `templates/allele/create.html`

Template for the `AlleleCreate` view. Renders a single-field form for the
allele's name plus a submit button, wrapped in the standard layout and
breadcrumb navigation.

### `templates/allele/detail.html`

Template for the `AlleleDetail` view. Renders a table of the allele's HCI ID,
name, CAR ID (as a link out to the ClinGen Allele Registry), and added date,
plus collapsible sections for any related curations and haplotypes.

### `templates/allele/list.html`

Template for the `AlleleList` view. Renders the breadcrumb, includes the
shared allele table partial, and provides a button that links to the create
view.

### `templates/allele/partials/table.html`

Reusable allele table fragment used by the list view and by the detail views
of related models (e.g., haplotype). Renders the HCI ID, name, CAR ID, and
added date, and initializes a `DataTable` for client-side sorting and search.

### `tests.py`

Tests for the create, detail, and list views. `AlleleCreateTest` patches
`fetch_allele_data` to mock the CAR API response and asserts that valid form
submissions persist an `Allele` with the CAR-supplied ID and the logged-in
user as `added_by`. `AlleleDetailTest` also verifies that related haplotypes
show up on the detail page.

### `urls.py`

URL routes for the app: `allele-create` (`create`), `allele-detail`
(`<slug:slug>/detail`), and `allele-list` (`list`).

### `views.py`

Class-based views for the app: `AlleleCreate` (overrides `form_valid` to
fetch CAR data, populate `car_id` and `added_by`, and warn the user if the
CAR call fails), `AlleleDetail`, and `AlleleList`. All views inherit from
`ProtectedViewMixin`.
