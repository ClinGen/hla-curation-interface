# `haplotype`

Django app that manages HLA haplotypes — ordered combinations of alleles across HLA
genes — within the HCI. It provides a `Haplotype` model that stores a many-to-many
relationship with alleles, derives a canonical tilde-separated name by sorting alleles
according to their chromosomal gene order, and supplies the full set of views, forms,
templates, and URL routes for creating, browsing, and auditing haplotypes.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers the `Haplotype` model with the Django admin site using `SimpleHistoryAdmin`,
showing `name`, `added_by`, and `added_at` in the list view, with search by name and
`added_by` and `added_at` as read-only fields.

### `apps.py`

Defines the `HaplotypeConfig` app configuration, setting `BigAutoField` as the default
primary key type and registering the app under the name `haplotype`.

### `constants/__init__.py`

Empty file; marks this directory as a Python package.

### `constants/models.py`

Defines `GENE_LIST`, an ordered list of HLA gene names on chromosome 6 arranged by
ascending chromosomal position, which is used to sort constituent alleles into a
canonical haplotype name.

### `fixtures/test_haplotypes.json`

Django fixture providing one sample `haplotype.haplotype` record (slug `H000001`, name
`A*01:02:03~B*04:05:06`) used by the test suite together with `test_alleles.json`.

### `forms.py`

Defines `HaplotypeForm`, a `ModelForm` for `Haplotype` that exposes only the `alleles`
field rendered as a `SelectMultiple` widget, allowing the user to select two or more
alleles when creating a haplotype.

### `models.py`

Defines the `Haplotype` model with a slug, a many-to-many `alleles` relation to `Allele`
(stored in the `haplotype_allele_map` join table), a computed `name` field, and audit
metadata. The `save` method auto-generates a zero-padded slug (`H000001` style).
Historical change tracking is provided via `simple_history`.

### `templates/haplotype/change.html`

Displays a single historical change record for a haplotype, with a breadcrumb trail back
through the haplotype list, detail, and history pages, and the change body rendered via
the shared `common/history/change_body.html` partial.

### `templates/haplotype/create.html`

Renders the "Add Haplotype" form, showing the alleles multi-select field (rendered via
the shared search select partial) and a submit button.

### `templates/haplotype/detail.html`

Shows the detail view for a single haplotype, displaying its HCI ID, name, and
timestamps. If the haplotype has associated curations or alleles, each is listed in a
collapsible section using the respective app's table partial.

### `templates/haplotype/history.html`

Shows the full edit history for a haplotype using the shared
`common/history/history_body.html` partial, with breadcrumbs to the list and detail
pages.

### `templates/haplotype/list.html`

Delegates to the `haplotype/partials/table.html` partial to render the haplotype
DataTable, and provides an "Add Haplotype" button below it.

### `templates/haplotype/partials/table.html`

Renders a DataTables table of haplotypes with columns for HCI ID (linked to the detail
page), name, and last-updated date. This partial is included by both the list page and
other apps that need to embed a haplotype table.

### `tests.py`

Contains `TestCase` classes for `HaplotypeCreate`, `HaplotypeDetail`, and
`HaplotypeList` views, verifying page content, access control, form validation,
canonical allele-order sorting, and duplicate-allele-combination detection.

### `urls.py`

Maps the five haplotype URL patterns — `create`, `<slug>/detail`, `<slug>/history`,
`<slug>/history/<id>/change`, and `list` — to their corresponding view classes.

### `views.py`

Implements five class-based views — `HaplotypeCreate`, `HaplotypeDetail`,
`HaplotypeHistory`, `HaplotypeChange`, and `HaplotypeList` — all protected by
`ProtectedViewMixin`. `HaplotypeCreate.form_valid` sorts the selected alleles by their
position in `GENE_LIST` to compute the canonical `~`-separated name, rejects duplicate
combinations, and sets `added_by`. `HaplotypeChange` uses `resolve_changes` to build a
diff for the selected history record.
