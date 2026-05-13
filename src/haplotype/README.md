# `haplotype`

This directory contains the `haplotype` Django app for the HLA Curation Interface
(HCI). The app manages HLA haplotypes, which are sets of HLA alleles that travel
together on the same chromosome. A `Haplotype` is built from existing `Allele`
records via a many-to-many relationship; when a curator selects the constituent
alleles, the app derives the haplotype's name by sorting the alleles by gene
location on chromosome 6 (using `GENE_LIST`) and joining them with `~` (e.g.,
`DRB1*15:01~DQB1*06:02`). Each record stores a human-readable slug ID, the
derived name, and metadata about who added it and when.

### `__init__.py`

Marks the directory as a Python package.

### `admin.py`

Registers the `Haplotype` model with Django's admin site and configures its
list display, search fields, and read-only fields (`added_by`, `added_at`).

### `apps.py`

Django `AppConfig` for the `haplotype` app.

### `constants/__init__.py`

Marks the directory as a Python package.

### `constants/models.py`

Defines `GENE_LIST`, the list of chromosome 6 genes ordered by genomic
location, used to sort the constituent alleles when deriving a haplotype's
name.

### `fixtures/test_haplotypes.json`

Django fixture containing test `Haplotype` records used by
`HaplotypeDetailTest` and `HaplotypeListTest`.

### `forms.py`

Defines `HaplotypeForm`, a `ModelForm` exposing the `alleles` many-to-many
field via a `SelectMultiple` widget.

### `models.py`

Defines the `Haplotype` model with `slug` (an `H######` human-readable ID
generated on save), `alleles` (M2M to `Allele`), `name`, `added_by`, and
`added_at`. Provides `get_absolute_url` pointing at the `haplotype-detail`
view.

### `templates/haplotype/create.html`

HTML template that renders the haplotype creation form for the
`HaplotypeCreate` view.

### `templates/haplotype/detail.html`

HTML template that renders the haplotype detail page for the `HaplotypeDetail`
view, including the haplotype's constituent alleles and any related curations.

### `templates/haplotype/list.html`

HTML template that renders the haplotype list for the `HaplotypeList` view.

### `templates/haplotype/partials/table.html`

Reusable partial that renders the haplotype list table.

### `tests.py`

Tests for the create, detail, and list views, including an assertion that
submitting two alleles produces a haplotype whose name is the gene-ordered,
`~`-joined concatenation of the allele names.

### `urls.py`

URL routes for the app: `haplotype-create`, `haplotype-detail`, and
`haplotype-list`.

### `views.py`

Class-based views for the app: `HaplotypeCreate` (overrides `form_valid` to
sort the selected alleles by gene location, build the haplotype name, and
record the user), `HaplotypeDetail`, and `HaplotypeList`. All views inherit
from `ProtectedViewMixin`.
