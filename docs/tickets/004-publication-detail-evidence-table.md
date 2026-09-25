# Render the Publication Detail Evidence Table with django-tables2

## The Problem

The original note asked why the evidence table on the publication detail page wasn't
using DataTables.js. That question is out of date: DataTables and jQuery were removed
from the project (commits `bcfafec` and `0c2524e`) in favor of django-tables2
(`docs/plans/003-search-list-view.md`). The underlying inconsistency is still there,
though. The allele, haplotype, and disease detail pages build `django_tables2` tables in
`get_context_data` (for example, `AlleleDetail` builds `CurationTable` and
`HaplotypeTable` and renders them with `{% render_table %}`). The publication detail
page, by contrast, loops over `object.evidence.all` in a hand-written `<table>` in
`src/publication/templates/publication/detail.html`. As a result, that table:

- can't be sorted or paginated, and doesn't use the shared `table is-fullwidth
  is-hoverable` styling;
- duplicates the classification labels in an `{% if sc == "DEF" %}...` chain instead of
  using `CLASSIFICATION_CHOICES`, as `CurationTable.render_classification` does;
- shows curation status as plain text with an ad hoc `/Published` suffix instead of the
  status tags that `CurationTable.render_status` renders. The suffix is appended when
  `evidence.curation.publication` (the `PublishedCuration` reverse relation) exists,
  even though the `Status.PUBLISHED` status already exists;
- runs one query per row for `curation`, `allele`, `haplotype`, and `disease`, because
  nothing calls `select_related`.

The goal is to make the publication detail page follow the same django-tables2 pattern
as the other detail pages.

## The Technical Plan

Add an `EvidenceTable` to `src/curation/tables.py`, next to `CurationTable`. Each row is
an `Evidence`, and the columns match what the page shows today: evidence ID (a link to
`evidence-detail`), curation ID (a link to `curation-detail`), allele, haplotype,
disease, curation status, and classification. The status and classification columns
reuse the rendering logic in `CurationTable`. Move that logic into module-level helper
functions that both tables call, so the tags and labels stay identical. In
`PublicationDetail.get_context_data`, build the table from
`obj.evidence.select_related("curation__allele", "curation__haplotype",
"curation__disease")`, configure it with `RequestConfig` and `prefix="evidence_"`, and
render it with `{% render_table evidence_table %}` inside the existing `<details>`
element.

The evidence table on the curation detail page
(`src/curation/templates/curation/partials/evidence/detail_table.html`) is also written
by hand. It is out of scope here because it has different columns and an edit button,
but it is a natural follow-up.

## Detailed Implementation

### Step 1 — Tests first

#### `src/publication/tests/test_views.py` — modify

Load `test_evidence.json` and the fixtures it depends on (`test_alleles.json`,
`test_diseases.json`, `test_publications.json`, `test_curations.json`, the same list
`src/curation/tests/test_views.py` uses) in a new `PublicationDetailEvidenceTest`. The
only evidence row (pk 1) points at publication 1 and curation C000001 (an allele
curation, status `INP`). Assert that:

- `response.context["evidence_table"]` is an `EvidenceTable`;
- the page links to the evidence detail and curation detail URLs;
- the curation's status tag and classification label appear;
- a publication with no evidence (P000002) does not render the Evidence section;
- `assertNumQueries` stays constant when a second evidence row is added.

#### `src/curation/tests/test_tables.py` — create

Add unit tests for `EvidenceTable`: the column sequence, and the status and
classification rendering for a curation with `ep_classification` set and for one that
falls back to `suggested_classification`.

### Step 2 — Add `EvidenceTable`

#### `src/curation/tables.py` — modify

Pull the bodies of `CurationTable.render_status` and `render_classification` out into
module-level functions (for example, `render_status_tag(value)` and
`render_classification_label(curation)`), and have `CurationTable` call them. Add
`EvidenceTable(tables.Table)` with `slug` as a `LinkColumn` to `evidence-detail` using
`kwargs={"curation_slug": A("curation__slug"), "evidence_slug": A("slug")}`, and
`curation` as a `LinkColumn` to `curation-detail`. Also add `curation__allele`,
`curation__haplotype`, and `curation__disease` columns with `default="------"`, plus
status and classification columns that call the shared helpers. Use the same
`Meta.attrs` as `CurationTable`.

#### `src/curation/README.md` — modify

Update the `tables.py` entry, and add an entry for `tests/test_tables.py`.

### Step 3 — Use it on the publication detail page

#### `src/publication/views.py` — modify

Give `PublicationDetail` a `get_context_data` that mirrors `AlleleDetail`: build
`EvidenceTable(... , prefix="evidence_")` from the `select_related` queryset, call
`RequestConfig(self.request).configure(...)`, and put it in `context["evidence_table"]`.

#### `src/publication/templates/publication/detail.html` — modify

Add `{% load django_tables2 %}`, as `allele/detail.html` does. Replace the hand-written
table inside `<details>` with `{% render_table evidence_table %}`. Keep the `{% if
object.evidence.all %}` guard, and make the section `open` by default to match the
allele and haplotype pages.

#### `src/publication/README.md` — modify

Update the `views.py` and `templates/publication/detail.html` entries.

## Sources

- Notes: "HCI: Figure out why the publication detail page evidence isn't using
  DataTables.js"
