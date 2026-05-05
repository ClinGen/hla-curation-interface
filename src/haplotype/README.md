# Haplotype

This directory contains the `haplotype` Django app for the HLA Curation
Interface (HCI). The app manages HLA haplotypes, which are sets of HLA alleles
that travel together on the same chromosome. A `Haplotype` is built from
existing `Allele` records via a many-to-many relationship; when a curator
selects the constituent alleles, the app derives the haplotype's name by
sorting the alleles by gene location on chromosome 6 (using `GENE_LIST`) and
joining them with `~` (e.g., `DRB1*15:01~DQB1*06:02`). Each record stores a
human-readable slug ID, the derived name, and metadata about who added it and
when.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `admin.py` — Registers the `Haplotype` model with Django's admin site and
  configures the list display, search fields, and read-only fields.
- `apps.py` — Django `AppConfig` for the `haplotype` app.
- `forms.py` — Defines `HaplotypeForm`, a `ModelForm` exposing the `alleles`
  many-to-many field via a `SelectMultiple` widget.
- `models.py` — Defines the `Haplotype` Django model with fields for `slug`,
  `alleles` (M2M to `Allele`), `name`, `added_by`, and `added_at`.
  Auto-generates a human-readable slug ID (`H######`) on save and provides
  `get_absolute_url`.
- `tests.py` — Tests for the create, detail, and list views, including
  assertions that submitting two alleles produces a haplotype whose name is
  the gene-ordered, `~`-joined concatenation of the allele names.
- `urls.py` — URL routes for the app: `haplotype-create`, `haplotype-detail`,
  and `haplotype-list`.
- `views.py` — Class-based views for the app: `HaplotypeCreate` (overrides
  `form_valid` to sort the selected alleles by gene location, build the
  haplotype name, and record the user), `HaplotypeDetail` (shows details for
  a single haplotype, including its constituent alleles and any related
  curations), and `HaplotypeList` (lists haplotypes). All views inherit from
  `ProtectedViewMixin`.

## Subdirectories

- `constants/` — Module-level constants: `models.py` defines `GENE_LIST`, the
  list of chromosome 6 genes ordered by genomic location, used to sort the
  alleles in a haplotype's name.
- `fixtures/` — Test fixtures: `test_haplotypes.json` provides the haplotype
  data loaded by `HaplotypeDetailTest` and `HaplotypeListTest`.
- `migrations/` — Django database migrations for the `Haplotype` model.
- `templates/haplotype/` — HTML templates for the app: `create.html`,
  `detail.html`, and `list.html`, plus `partials/table.html`, the reusable
  haplotype table fragment used by the list view.
