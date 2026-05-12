# Allele

This directory contains the `allele` Django app for the HLA Curation Interface
(HCI). The app is responsible for managing HLA alleles within the system,
including creating new allele records (with data fetched from the ClinGen
Allele Registry), viewing allele details, and listing alleles. Each allele
record stores the user-supplied name (e.g., `DRB3*03:01:01`), the corresponding
ClinGen Allele Registry (CAR) ID, a human-readable slug ID, and metadata about
who added it and when.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers the `Allele` model with Django's admin site and
  configures the list display, search fields, and read-only fields.
- `apps.py` — Django `AppConfig` for the `allele` app.
- `clients.py` — Functions that interact with the ClinGen Allele Registry
  third-party service: `fetch_allele_data` retrieves allele data from the CAR
  HTTP endpoint, and `get_car_id` extracts the CAR ID from the response.
- `forms.py` — Defines `AlleleForm`, a `ModelForm` exposing the `name` field of
  the `Allele` model for the create view.
- `models.py` — Defines the `Allele` Django model with fields for `slug`,
  `name`, `car_id`, `added_by`, and `added_at`. Auto-generates a human-readable
  slug ID on save and provides `get_absolute_url`.
- `tests.py` — Tests for the create, detail, and list views, including a mock
  of the CAR API response and assertions about the resulting `Allele`
  instances.
- `urls.py` — URL routes for the app: `allele-create`, `allele-detail`, and
  `allele-list`.
- `views.py` — Class-based views for the app: `AlleleCreate` (creates an
  allele, fetching CAR data and recording the user), `AlleleDetail` (shows
  details for a single allele), and `AlleleList` (lists alleles). All views
  inherit from `ProtectedViewMixin`.

## Subdirectories

- `fixtures/` — Test fixtures (e.g., `test_alleles.json`) loaded by the test
  cases.
- `migrations/` — Django database migrations for the `Allele` model.
- `templates/allele/` — HTML templates for the app: `create.html`,
  `detail.html`, and `list.html`, plus `partials/table.html`, a reusable
  allele table fragment used by the list view.
