# Search List View

## The Problem

Every list view in the HCI — alleles, diseases, publications, haplotypes, curations, and
published curations — uses DataTables to provide search, sorting, and column display.
The shared `common/history/history_body.html` partial uses DataTables for change history
tables across every model. This works, but it has a few downsides. All records are
fetched from the database and sent to the browser on every page load; DataTables then
searches and sorts entirely client-side in JavaScript. The rendering logic for each
table lives in a per-app template partial (e.g., `allele/partials/table.html`), which
makes custom column rendering verbose, difficult to reuse, and spread across many files.
There is no consistent pattern across apps.

The goal is to replace all DataTables-based tables — both list views and history tables
— with a single reusable structure powered by django-tables2, and to replace the
client-side search in list views with a server-side active search bar powered by HTMX.

## The Technical Plan

There are four moving parts: a base view class, per-app table classes, two shared
templates, and a small adjustment to each app's existing list template. Here is how they
fit together.

**Table classes.** Right now, the columns of each table — what fields appear, how they
are formatted, and whether a value links somewhere — are defined in HTML template
partials scattered across the apps. The new approach moves that logic into Python. Each
app gets a `tables.py` file with a class that describes its table: which columns to
show, what label each column header gets, whether a column is sortable, and how to
render any value that needs special treatment (a link, a status tag, an external URL).
The library that powers this is django-tables2, which knows how to turn one of these
classes into a rendered HTML table.

**`SearchListView`.** This is a new base class that all six list views will inherit
from. It does three things. First, it reads the `q` query parameter from the URL and, if
one is present, narrows the database query to only records that contain that string in
any of the fields the subclass has nominated as searchable. Second, it passes the
resulting records to the app's table class, which renders them as HTML. Third — and this
is the key to the live-search behavior — it looks at the incoming request to decide what
to return. A normal page load gets the full page: navbar, heading, search input, table,
and all. A request that came from the search input (which HTMX marks with a special
header) gets only the table and result count, no full page. This means a single URL and
a single view handles both cases.

**Two shared templates.** `search_input.html` renders the search bar. It is a plain text
input wired with HTMX so that, 500 milliseconds after the user stops typing, it sends
the current value to the server and swaps the results area with whatever comes back —
without reloading the page. `search_results.html` is that results area: a result count
line, the rendered table, and an empty-state message for when nothing matches. Both the
initial page load and every subsequent keystroke render the same partial, so there is no
duplicated markup.

**Updated list templates.** Each app's existing `list.html` changes in one place: the
line that currently pulls in the old `partials/table.html` is replaced with the search
input and a wrapper `<div>` around the results partial. Everything else — the page
heading, breadcrumbs, and action buttons — stays exactly as it is.

**History tables.** The history table that appears on every model's history page
(showing who changed the record, what kind of change it was, and when) follows a simpler
version of the same pattern. A single `HistoryTable` class in `common/tables.py` defines
those three columns. Each history view constructs one, passing in the URL name and slug
values needed to build the per-row links, and the existing `history_body.html` partial
renders it. History views do not need a search bar, so they do not use `SearchListView`.

## Alternatives

**A dedicated search endpoint per model.** Rather than sending the search query to the
same URL as the list page and detecting the HTMX header server-side, we considered
giving each model a separate `/search/` sub-URL that would return only the table
partial. This would have made the routing explicit: the list page URL always returns a
full page and the search URL always returns a fragment. We rejected it because it
doubles the number of URL patterns and view classes for no meaningful gain. The
`HX-Request` header reliably distinguishes the two cases, and using the same URL means
the browser address bar stays meaningful — a user can bookmark or share a filtered URL
and get the right results back.

**A fully generic column renderer.** An early idea was to make `SearchListView` generic
enough that subclasses could declare a list of field names and the view would
automatically render those fields as columns, iterating over them in a shared template.
This would have meant zero per-app templates or table classes. We ruled it out because
custom rendering is the norm in this codebase, not the exception: every table has at
least one link column, most have date formatting, and several have conditional tags or
external linkouts. A generic iterator would have handled only a minority of cells
correctly and required per-field escape hatches immediately, at which point it is no
simpler than per-app table classes.

**Keeping column rendering in templates.** Even after ruling out a fully generic
renderer, we considered defining per-app table classes in Python but keeping the actual
cell HTML inside template snippets included via `TemplateColumn`. This preserves the
current pattern where presentation lives in `.html` files. We decided against it because
the existing template partials — the classification conditionals in the curation table,
the linkout logic, the status tag switching — are already verbose and hard to follow.
Moving this logic into Python `render_*` methods makes it easier to read and keeps it in
one place per model rather than split across a table class and a handful of small
template files.

**Putting `search_fields` on the table class.** It would be natural to annotate each
column as searchable or not on the `Table` class itself, keeping all column-related
configuration in one place. We rejected this because the search filter is a queryset
concern, not a display concern: it determines which database rows are fetched, not how
those rows look. The `Table` class should not need to know how it is queried. Keeping
`search_fields` on the view class preserves a clean boundary: the view owns data
retrieval, the table class owns presentation.

**Deferring sorting and pagination.** The initial plan treated sorting and pagination as
future work, noting that django-tables2 supports them but not committing to implementing
them now. We reversed this because the marginal cost of including them from the start is
low: `SingleTableMixin` handles the `?sort=` and `?page=` query parameters automatically
once the table class is in place, and `hx-boost` on the results container makes both
pagination links and sort header clicks HTMX-aware with no custom template required.
Building the infrastructure and then omitting a nearly-free feature would have meant
revisiting every table class and template later.

**A custom pagination template.** To make pagination links trigger HTMX swaps rather
than full page reloads, we considered writing a custom django-tables2 pagination
template that adds `hx-get`, `hx-target`, and `hx-push-url` attributes to each link
explicitly. This gives the most control but requires maintaining a non-trivial template
override. We chose `hx-boost` on the results container instead: a single attribute on a
wrapper element intercepts all anchor clicks inside it and converts them to HTMX
requests, which achieves the same effect with far less code.

**Leaving history tables on DataTables.** The history table in `history_body.html` was
initially out of scope on the grounds that it is a different pattern — a partial
included by detail views rather than a standalone list view — and does not need a search
bar. We brought it into scope because excluding it would mean DataTables could never be
fully removed from the project: the CSS and JS would remain in `layouts/base.html`
indefinitely. Migrating the history table is straightforward since a single
`HistoryTable` class in `common` serves all apps, and the history views are simple
enough that the change is low-risk.

## Detailed Implementation

The steps below must be followed in order. Each step lists every file that is created,
changed, or deleted, and explains why that file is touched. Files that are noted as
changed in an earlier step and touched again in a later step are called out explicitly
so that nothing is missed.

### Step 1: Install django-tables2 and register it

**`pyproject.toml` — CHANGE.** Add `django-tables2` as a dependency. It is not yet
installed in the project.

**`config/settings/base.py` — CHANGE.** Add `"django_tables2"` to `INSTALLED_APPS`,
after `"django.contrib.staticfiles"` and before the project's own apps. django-tables2
ships its own template tags and default table templates that Django's app loader must be
able to find; they are not available unless the app is registered here.

### Step 2: Write `SearchListView` and the two shared search templates

**`common/views.py` — CREATE.** This file does not currently exist. It will define
`SearchListView`, which inherits from `SingleTableMixin` (django-tables2) and `ListView`
(Django). It overrides `get_queryset` to read the `q` GET parameter; when `q` is
non-empty, it builds an OR-combined set of `__icontains` lookups across the field names
listed in the subclass's `search_fields` attribute and applies them as a single
`filter()` call. It overrides `get_template_names` to return
`common/partials/search_results.html` when the `HX-Request` header is present, and the
view's own `template_name` otherwise. It adds `query` (the current search string) and
`result_count` (the count after filtering) to the template context.

Note on protection: `SearchListView` does **not** include `ProtectedViewMixin`. The
draft plan proposed including it here, but the `repo` app's `PublishedCurationList` is a
public view and cannot subclass a protected class. Instead, every list view in a
protected app will declare `ProtectedViewMixin` explicitly:
`class AlleleList(ProtectedViewMixin, SearchListView)`. The repo list view omits it.

**`common/templates/common/partials/search_input.html` — CREATE.** The `partials/`
subdirectory does not currently exist under `common/templates/common/`. This template
renders a Bulma-styled text input with the following HTMX attributes: `hx-get` set to
`request.path`, `hx-target` set to `#search-results`, `hx-trigger` set to
`keyup changed delay:500ms`, and `name` set to `q`. Its `value` attribute is populated
from the `query` context variable so the search term is preserved on full-page loads
when a `?q=` parameter is already in the URL. A single shared partial means the search
bar looks and behaves identically on every list page, and any change to its behavior
(e.g., adjusting the debounce delay) is made in exactly one place.

**`common/templates/common/partials/search_results.html` — CREATE.** This template
renders the HTMX-swappable results area: a result-count line ("N result(s)"), the
django-tables2 table via `{% render_table table %}`, and an empty-state message when the
table has no rows. It is also `{% include %}`d inside each app's full-page list template
so that the initial page load and every subsequent HTMX response render from the same
template. This eliminates any risk of drift between the two code paths. The results
`<div>` carries `hx-boost="true"` and `hx-target="#search-results"` so that
django-tables2's pagination links and sortable column headers trigger HTMX swaps rather
than full page reloads.

### Step 3: Write `HistoryTable` and migrate all history views

All eight history views in the project share `common/history/history_body.html`. That
partial currently iterates over a `history` queryset in HTML and initialises DataTables
in an inline `<script>` block. Because the partial is shared, migrating one history view
in isolation is not feasible — changing the partial would break every other history page
at the same time. All history views are therefore migrated together in this step, before
any list views are touched.

**`common/tables.py` — CREATE.** This file does not currently exist. It defines
`HistoryTable`, a django-tables2 `Table` subclass with three columns: Changed By, Change
(a link), and Date. The link in the Change column must point to a different URL in every
app (`allele-change`, `curation-change`, `repo-change`, etc.) and must embed one or two
slug values depending on the model. To handle this, `HistoryTable.__init__` accepts
`change_url_name`, `change_url_slug1` (optional), and `change_url_slug2` (optional) as
keyword arguments, stores them on the instance, and uses them in `render_history_type()`
to construct the correct URL for each row. Evidence history is the only case that
requires two slugs (curation slug + evidence slug); all other history views require one
or none.

**`common/templates/common/history/history_body.html` — CHANGE.** Replace the `<table>`
block, the `{% for record in history %}` loop, and the inline `<script>` block with
`{% load django_tables2 %}` and `{% render_table history_table %}`, followed by the
existing no-records message. The `history_table` context variable is the `HistoryTable`
instance constructed by the calling view. The template variables `table_id`,
`change_url_name`, `change_url_slug1`, and `change_url_slug2` — which the old partial
accepted via `{% include ... with ... %}` — are no longer used and can be removed from
every calling template.

The following views and templates all change for the same reason: each history view must
now construct a `HistoryTable` instance (instead of a queryset keyed as `history`) and
add it to context as `history_table`; each history template must drop the `with ...`
arguments from its `{% include %}` call.

**`allele/views.py` — CHANGE** (`AlleleHistory.get_context_data`)**.** Replace
`context["history"] = obj.history.all()` with a `HistoryTable` constructed with
`change_url_name="allele-change"` and `change_url_slug1=obj.slug`, assigned as
`context["history_table"]`.

**`allele/templates/allele/history.html` — CHANGE.** Remove `table_id`,
`change_url_name`, and `change_url_slug1` from the
`{% include "common/history/history_body.html" with ... %}` call.

**`disease/views.py` — CHANGE** (`DiseaseHistory.get_context_data`)**.** Same pattern.
`change_url_name="disease-change"`, slug is `obj.slug`.

**`disease/templates/disease/history.html` — CHANGE.** Same cleanup as
`allele/history.html`.

**`haplotype/views.py` — CHANGE** (`HaplotypeHistory.get_context_data`)**.** Same
pattern. `change_url_name="haplotype-change"`.

**`haplotype/templates/haplotype/history.html` — CHANGE.** Same cleanup.

**`publication/views.py` — CHANGE** (`PublicationHistory.get_context_data`)**.** Same
pattern. `change_url_name="publication-change"`.

**`publication/templates/publication/history.html` — CHANGE.** Same cleanup.

**`curation/views.py` — CHANGE** (`CurationHistory.get_context_data` and
`EvidenceHistory.get_context_data`)**.** `CurationHistory`:
`change_url_name="curation-change"`, `change_url_slug1=obj.slug`. `EvidenceHistory`:
`change_url_name="evidence-change"`, `change_url_slug1` is the curation slug (already in
`self.kwargs["curation_slug"]`), and `change_url_slug2` is the evidence slug
(`obj.slug`). This is the only two-slug case.

**`curation/templates/curation/history.html` — CHANGE.** Same cleanup.

**`curation/templates/evidence/history.html` — CHANGE.** Same cleanup — this template
previously passed both `change_url_slug1` and `change_url_slug2`, both of which are now
encoded in the `HistoryTable` instance.

**`repo/views.py` — CHANGE** (`PublishedCurationHistory.get_context_data`)**.**
`change_url_name="repo-change"`, `change_url_slug1=self.object.curation.slug`. The
existing `context["history"] = self.object.history.all()` line is replaced by the
`HistoryTable` instance.

**`repo/templates/repo/history.html` — CHANGE.** Same cleanup.

**`auth_/views.py` — CHANGE** (`profile_history` function view)**.** The profile history
view currently passes a `history` queryset to its template. Replace it with a
`HistoryTable` instance constructed with `change_url_name="profile-change"` and no slug
arguments (profile change URLs are routed by `history_id` alone). Pass it as
`history_table` in the context dict.

**`auth_/templates/auth_/history.html` — CHANGE.** Same cleanup.

### Step 4: Migrate the `allele` list view

**`allele/tables.py` — CREATE.** Define `AlleleTable` with four columns: `slug` (a
`LinkColumn` resolving to `allele-detail`), `name`, `car_id` (overrides
`render_car_id()` to render `common/linkout.html` with the CAR registry URL when a CAR
ID is present, and a placeholder dash otherwise), and `updated_at` (a `DateColumn`
formatted `Y-m-d`). The CAR ID column is marked `orderable=False` because it is not a
simple sortable field. The column definitions here replace the rendering logic that
currently lives in `allele/partials/table.html`.

**`allele/views.py` — CHANGE** (`AlleleList`)**.** Change the parent classes from
`ProtectedViewMixin, ListView` to `ProtectedViewMixin, SearchListView`. Add
`table_class = AlleleTable`, `search_fields = ["slug", "name", "car_id"]`, and
`table_pagination = {"per_page": 25}`. The `ProtectedViewMixin` import stays because
other views in this file still use it.

**`allele/templates/allele/list.html` — CHANGE.** Replace the single
`{% include "allele/partials/table.html" with alleles=object_list %}` line with
`{% include "common/partials/search_input.html" %}` followed by
`<div id="search-results">{% include "common/partials/search_results.html" %}</div>`.
The breadcrumb, box wrapper, and "Add Allele" button are unchanged.

**`allele/templates/allele/partials/table.html` — DELETE.** This file's rendering logic
has moved into `AlleleTable`. It is referenced in one other place —
`haplotype/detail.html` — which is updated below before this file is deleted.

**`haplotype/views.py` — CHANGE** (`HaplotypeDetail.get_context_data`)**.**
`haplotype/detail.html` embeds `allele/partials/table.html` at line 73 to show the
haplotype's constituent alleles. Now that the partial is deleted, `HaplotypeDetail` must
construct an `AlleleTable` from `self.object.alleles.all()` and add it to context as
`allele_table`. This requires importing `AlleleTable` from `allele.tables`.

**`haplotype/templates/haplotype/detail.html` — CHANGE.** Replace
`{% include "allele/partials/table.html" with alleles=object.alleles.all %}` at line 73
with `{% load django_tables2 %}{% render_table allele_table %}`.

### Step 5: Migrate the `disease` list view

**`disease/tables.py` — CREATE.** Define `DiseaseTable` with four columns: `slug`
(`LinkColumn` to `disease-detail`), `name`, `mondo_id` (overrides `render_mondo_id()` to
render `common/linkout.html` using `record.iri` as the URL when both `iri` and
`mondo_id` are present, and a dash otherwise), and `updated_at` (`DateColumn`, `Y-m-d`).
`mondo_id` is marked `orderable=False`.

**`disease/views.py` — CHANGE** (`DiseaseList`)**.** Same substitution as `AlleleList`:
`ProtectedViewMixin, SearchListView`, add `table_class = DiseaseTable`,
`search_fields = ["slug", "name", "mondo_id"]`, `table_pagination = {"per_page": 25}`.

**`disease/templates/disease/list.html` — CHANGE.** Unlike `allele/list.html`, this
template has no separate `partials/table.html` — the `<table id="disease-list-table">`
block and the `<script>` tag at the bottom are inline. Replace both with the search
input include and the results div. The breadcrumb, box wrapper, and "Add Disease" button
are unchanged.

### Step 6: Migrate the `haplotype` list view

**`haplotype/tables.py` — CREATE.** Define `HaplotypeTable` with three columns: `slug`
(`LinkColumn` to `haplotype-detail`), `name`, and `updated_at` (`DateColumn`, `Y-m-d`).
Search fields: `["slug", "name"]`.

**`haplotype/views.py` — CHANGE** (`HaplotypeList`)**.** This file was already changed
in Step 4 to update `HaplotypeDetail`. Now also change `HaplotypeList` to inherit from
`ProtectedViewMixin, SearchListView` and add `table_class = HaplotypeTable`,
`search_fields`, and `table_pagination`.

**`haplotype/templates/haplotype/list.html` — CHANGE.** Replace
`{% include "haplotype/partials/table.html" with haplotypes=object_list %}` with the
search input and results div.

**`haplotype/templates/haplotype/partials/table.html` — DELETE.** This partial is
referenced in two places: `haplotype/list.html` (updated above) and `allele/detail.html`
at line 85. The `allele/detail.html` update is below.

**`allele/views.py` — CHANGE** (`AlleleDetail.get_context_data`)**.** This file was
already changed in Step 3 to update `AlleleHistory`. Now also update `AlleleDetail` to
construct a `HaplotypeTable` from `self.object.haplotypes.all()` and add it as
`haplotype_table`. Requires importing `HaplotypeTable` from `haplotype.tables`.

**`allele/templates/allele/detail.html` — CHANGE.** Replace
`{% include "haplotype/partials/table.html" with haplotypes=object.haplotypes.all %}` at
line 85 with `{% load django_tables2 %}{% render_table haplotype_table %}`.

### Step 7: Migrate the `publication` list view

**`publication/tables.py` — CREATE.** Define `PublicationTable` with seven columns:
`slug` (`LinkColumn` to `publication-detail`), `title` (a `TemplateColumn` or
`render_title()` method that wraps the value in `<i>` tags), `author`,
`publication_year`, `pubmed_id`, `doi`, and `updated_at` (`DateColumn`, `Y-m-d`). Unlike
in the detail view, the list table renders `pubmed_id` and `doi` as plain text rather
than external links — those linkouts belong on the detail page. Search fields:
`["slug", "title", "author", "doi", "pubmed_id"]`.

**`publication/views.py` — CHANGE** (`PublicationList`)**.** This file was already
changed in Step 3 to update `PublicationHistory`. Now also change `PublicationList` to
`ProtectedViewMixin, SearchListView` and add `table_class`, `search_fields`, and
`table_pagination`.

**`publication/templates/publication/list.html` — CHANGE.** Like `disease/list.html`,
this template has no separate partial — the `<table id="publication-list-table">` block
and `<script>` tag are inline. Replace both with the search input and results div.

### Step 8: Migrate the `curation` list view

This is the most complex step. The curation list table has more conditional rendering
logic than any other. The curation partial is also embedded in four templates outside
the curation app itself, so deleting it has downstream effects on `allele`, `haplotype`,
`disease`, and `core`. The history views for `CurationHistory` and `EvidenceHistory`
were already migrated in Step 3.

**`curation/tables.py` — CREATE.** Define `CurationTable` with eight columns: `slug`
(`LinkColumn` to `curation-detail`), `curation_type` (uses `get_curation_type_display`),
`allele`, `haplotype`, `disease`, `status`, `classification`, and `updated_at`
(`DateColumn`).

The `status` column overrides `render_status()` to render `common/tags/in_progress.html`
or `common/tags/done.html` based on the field value — the same tag partials already used
elsewhere in the project.

The `classification` column overrides `render_classification()` to reproduce the
multi-way conditional currently in `curation/partials/table.html` lines 30–44: if
`ep_classification` is set, use `get_ep_classification_display`; otherwise, map the
`suggested_classification` code to its display string. Moving this logic into a Python
method makes it easier to read and ensures it only exists in one place.

Search fields: `["slug", "allele__name", "haplotype__name", "disease__name"]`. FK
traversal in `__icontains` lookups works transparently in Django's ORM, so searching for
a disease name or allele name requires no special handling.

**`curation/views.py` — CHANGE** (`CurationList`)**.** This file was already changed in
Step 3 to update `CurationHistory` and `EvidenceHistory`. Now also change `CurationList`
from `ProtectedViewMixin, ListView` to `ProtectedViewMixin, SearchListView`, and add
`table_class = CurationTable`, `search_fields`, and `table_pagination`.

**`curation/templates/curation/list.html` — CHANGE.** Replace
`{% include "curation/partials/table.html" with curations=object_list %}` with the
search input and results div.

**`curation/templates/curation/partials/table.html` — DELETE.** This is the most widely
referenced partial in the project. It appears in five templates: `curation/list.html`
(updated above), `allele/detail.html` (line 78), `haplotype/detail.html` (line 66),
`disease/detail.html` (line 72), and `core/home.html` (line 107). All four remaining
usages are updated below before this file is deleted.

**`allele/views.py` — CHANGE** (`AlleleDetail.get_context_data`)**.** This file was
already changed in Steps 3 and 6. Now also construct a `CurationTable` from
`self.object.curations.all()` and add it as `curation_table`. Requires importing
`CurationTable` from `curation.tables`.

**`allele/templates/allele/detail.html` — CHANGE.** This file was already changed in
Step 6. Now also replace
`{% include "curation/partials/table.html" with curations=object.curations.all %}` at
line 78 with `{% render_table curation_table %}`. The `{% load django_tables2 %}` tag is
already present from Step 6.

**`haplotype/views.py` — CHANGE** (`HaplotypeDetail.get_context_data`)**.** This file
was already changed in Steps 3 and 4. Now also construct a `CurationTable` from
`self.object.curations.all()` and add it as `curation_table`.

**`haplotype/templates/haplotype/detail.html` — CHANGE.** This file was already changed
in Step 4. Now also replace
`{% include "curation/partials/table.html" with curations=object.curations.all %}` at
line 66 with `{% render_table curation_table %}`.

**`disease/views.py` — CHANGE** (`DiseaseDetail.get_context_data`)**.** This file was
already changed in Step 3 and Step 5. Now also construct a `CurationTable` from
`self.object.curations.all()` and add it as `curation_table`.

**`disease/templates/disease/detail.html` — CHANGE.** Replace
`{% include "curation/partials/table.html" with curations=object.curations.all %}` at
line 72 with `{% load django_tables2 %}{% render_table curation_table %}`.

**`core/views.py` — CHANGE** (`home` function view)**.** The home page shows the current
user's curations when they are logged in. Currently this is handled entirely in the
template via `user.curations_added.all`. With django-tables2, the table instance must be
constructed in the view. When the user is authenticated, construct a `CurationTable`
from `request.user.curations_added.all()` and add it as `curation_table`; otherwise pass
`None`. Requires importing `CurationTable` from `curation.tables`.

**`core/templates/core/home.html` — CHANGE.** Replace
`{% include "curation/partials/table.html" with curations=user.curations_added.all %}`
at line 107 with `{% load django_tables2 %}{% render_table curation_table %}`. Keep the
surrounding `{% if user.is_authenticated and curation_table %}` guard.

### Step 9: Migrate the `repo` list view

**`repo/tables.py` — CREATE.** Define `PublishedCurationTable` with eight columns. Seven
mirror the curation list columns, accessed through the `curation` FK: the ID
`LinkColumn` resolves to `repo-detail` using `record.curation.slug`, the type column
uses `get_curation_type_display`, and the allele, haplotype, disease, classification,
and updated columns follow the same pattern. The eighth column is Actions, implemented
as a `TemplateColumn` that renders the per-row JSON download button (currently at lines
63–67 of `repo/list.html`). The Actions column is marked `orderable=False`. Search
fields:
`["curation__slug", "curation__allele__name", "curation__haplotype__name", "curation__disease__name"]`.

**`repo/views.py` — CHANGE** (`PublishedCurationList`)**.** This file was already
changed in Step 3. Now also change `PublishedCurationList` from `ListView` to
`SearchListView` — without `ProtectedViewMixin`, since the repo is a public view. Add
`table_class = PublishedCurationTable`, `search_fields`, and `table_pagination`.

**`repo/templates/repo/list.html` — CHANGE.** Replace the inline
`<table id="published-curation-list-table">` block and the trailing `<script>` tag with
the search input include and the results div. The "Download All as JSON" button above
the table is unchanged.

### Step 10: Remove DataTables from the base layout

At this point every table in the application — list views, history tables, and the
related-object tables embedded in detail pages — is rendered by django-tables2. No page
emits a `new DataTable(...)` call.

**`templates/layouts/base.html` — CHANGE.** Remove the `<link>` tag for
`hci/css/dataTables.dataTables.min.css`, and the `<script>` tags for
`hci/js/jquery.min.js` and `hci/js/dataTables.min.js`. jQuery is present only as a
DataTables dependency; once DataTables is gone, jQuery can be removed too. Confirm that
no other feature in the project depends on jQuery before removing it. The HTMX and
Choices.js scripts are unaffected.

### Step 11: Write tests for `SearchListView`

The existing list-view test classes (e.g., `AlleleListTest`, `DiseaseListTest`) each
inherit `ProtectedViewTestMixin`, which verifies access control, correct template usage,
and that expected column headers and row values appear in the response. These tests
still pass after the migration and implicitly confirm that django-tables2 is rendering
the table correctly. However, the two behaviors that are entirely new — server-side
search filtering and HTMX partial responses — have no test coverage at all.

**`common/tests.py` — UPDATE.** This file defines `SearchListViewTest`, a `TestCase`
subclass that exercises `SearchListView` directly using Django's test client against the
allele list view as a representative endpoint. This avoids mocking the view class and
tests the full request-response cycle. It requires the `test_alleles` fixture (already
used by `AlleleListTest`) so that records exist in the database.

The test class covers four cases:

1. **Full-page response on a normal GET.** A GET to `/allele/list/` without the
   `HX-Request` header must use `allele/list.html`, not the partial. Verifies that the
   HTMX partial path is not triggered for ordinary browser navigations.

2. **Partial response when `HX-Request` is present.** A GET with
   `HTTP_HX_REQUEST="true"` (Django's header format for `HX-Request`) must use
   `common/partials/search_results.html` and must not use `allele/list.html`.

3. **Search filtering returns only matching rows.** A GET with `?q=A*01:02:03` (the
   allele name in the fixture) must include the matching row's ID and must include a
   result-count string like "1 result". A GET with `?q=zzz_no_match` must include "0
   results" and must not include the matching allele's ID.

4. **Empty query returns all rows.** A GET with `?q=` (empty string) must behave
   identically to a GET with no `q` parameter at all — the queryset is not filtered, and
   all fixture records appear.

Each test logs in as a user with full curation permissions (PHI agreement signed,
curation permissions granted) to satisfy `ProtectedViewMixin`, following the same
pattern used by every other list-view test in the project.
