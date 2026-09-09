# `haplotype`

This Django app manages HLA haplotypes, which are named combinations of two or more alleles joined by `~` (e.g., `DRB1*15:01~DQB1*06:02`). It provides the full CRUD surface for haplotypes, including creation with automatic name derivation, detail and list views, and change history tracking via `django-simple-history`.

### `__init__.py`

Empty file that marks this directory as a Python package.

### `admin.py`

Registers the `Haplotype` model with the Django admin site using `SimpleHistoryAdmin`, exposing name, submitter, and submission date in the list view and enabling history tracking.

### `apps.py`

Defines the `HaplotypeConfig` app configuration, setting the app name to `haplotype` and specifying `BigAutoField` as the default primary key type.

### `constants/__init__.py`

Empty file that makes `constants` a Python subpackage.

### `constants/models.py`

Defines `GENE_LIST`, an ordered list of HLA gene names sorted by their chromosomal position on chromosome 6 (sourced from hla.alleles.org). This list is used when constructing a haplotype's canonical name by sorting constituent alleles into genomic order.

### `fixtures/test_haplotypes.json`

Django fixture containing a single sample `Haplotype` record (`H000001`, `A*01:02:03~B*04:05:06`) used to seed the database during tests.

### `forms.py`

Defines `HaplotypeForm`, a `ModelForm` for the `Haplotype` model that exposes only the `alleles` field rendered as a multi-select widget.

### `models.py`

Defines the `Haplotype` model with a slug-based human-readable ID (e.g., `H000001`), a many-to-many relationship to `Allele`, a unique `name` field, provenance fields (`added_by`, `added_at`, `updated_at`), and full change history via `HistoricalRecords`. The slug is auto-generated from the primary key on first save.

### `tables.py`

Defines `HaplotypeTable` using `django-tables2`, displaying the haplotype's ID (as a link to the detail view), name, and last-updated date in a styled Bulma table.

### `templates/haplotype/change.html`

Renders the detail view for a single history record on a haplotype, showing what changed and when, with breadcrumb navigation back through the list, detail, and history views.

### `templates/haplotype/create.html`

Renders the haplotype creation form with a multi-select alleles field and a submit button, under a breadcrumb trail leading back to the home page.

### `templates/haplotype/detail.html`

Renders a haplotype's detail page, showing its ID, name, and timestamps in a summary table, along with collapsible `django-tables2` tables for its associated alleles and curations.

### `templates/haplotype/history.html`

Renders the full change history for a haplotype by delegating to the shared `common/history/history_body.html` partial, with breadcrumb navigation back to the list and detail views.

### `templates/haplotype/list.html`

Renders the haplotype search page with a search input, a results table populated via the shared search partials, and a link to the haplotype creation page.

### `tests.py`

Contains `TestCase` classes for the create, detail, and list views, verifying access control, correct template rendering, form validation (including duplicate detection and allele-order normalization), and successful haplotype creation.

### `urls.py`

Defines the five URL routes for the app: `create`, `<slug>/detail`, `<slug>/history`, `<slug>/history/<history_id>/change`, and `list`.

### `views.py`

Implements the five class-based views for the app. `HaplotypeCreate` derives the canonical haplotype name by sorting selected alleles using `GENE_LIST` and rejects duplicates. `HaplotypeDetail` populates allele and curation sub-tables. `HaplotypeHistory` and `HaplotypeChange` expose the `django-simple-history` audit trail. `HaplotypeList` provides paginated, searchable listing via `SearchListView`.
