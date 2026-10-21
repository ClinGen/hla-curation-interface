# `repo`

This Django app implements HLArepo, the public-facing repository of published HLA curations. Its pages extend `layouts/public.html`, which has no curator navigation or other links that need a login. It handles the `PublishedCuration` model (which wraps a completed `Curation`), exposes searchable list and detail views, tracks full change history via `django-simple-history`, and provides JSON download endpoints for individual or bulk export of published curation data.

### `__init__.py`

Empty file that marks `repo` as a Python package.

### `admin.py`

Registers `PublishedCuration` with the Django admin site using `SimpleHistoryAdmin`, displaying the associated curation, publisher, publication timestamp, and version in the list view.

### `apps.py`

Defines the `RepoConfig` app configuration, setting the app name to `repo` and the default auto field to `BigAutoField`.

### `constants.py`

Defines `PUBLIC_CURATION_FIELDS` and `PUBLIC_EVIDENCE_FIELDS`, the model fields shown in HLArepo and the JSON export. They're the single source of truth: the serializers' column maps must name exactly these fields (a test checks), and the forms mark these fields with a public badge. `needs_review` and every `*_notes` field on `Evidence` stay internal.

### `models.py`

Defines the `PublishedCuration` model, which links one-to-one to a `Curation` and records who published it, when, and at what version. Change history is tracked automatically via `HistoricalRecords`.

### `lineage.py`

Builds a published curation's family tree for its detail page. `build_lineage` walks `copied_from` up to the original, then down through every published update (oldest first), leaving out unpublished copies. Each `LineageNode` gets its box-drawing prefix, drawn like the `tree` command, and is marked if it's the current page or the newest in the family. The `Lineage` also carries a plain-text description that states every update relationship, for readers who can't see the tree. It returns `None` for a curation with no published relatives.

### `serializers.py`

Provides `serialize_published_curation` and `serialize_evidence`, plain functions that convert `PublishedCuration` and `Evidence` instances to plain Python dictionaries suitable for JSON export. Each curation is one flat object keyed by `curation_id`, with its evidence in an `evidence` list. `public_evidence` decides which evidence is public: only evidence included in the score, since HLArepo records no reason for an exclusion and excluded evidence may never have been finished. Every public output uses it. Coded values are their display labels (for example, `Published` and the classification as shown on the page), since the people who download the JSON aren't all programmers. Curator identities aren't exported, so there's no `published_by` key. The taskforce and evidence data fields are the ones named in `CLASSIFICATION_COLUMNS` and `EVIDENCE_COLUMNS`, which must match the public field lists in `constants.py`. Decimals are written the way a person would write them, by `format_decimal`, which the CSV download also uses. The export includes each allele's CAR ID (including haplotype member alleles), the disease IRI, the taskforce override reason, and the taskforce review date as an ISO date or `null`. It also builds rows for flat files, with readable column names and readable values: choice labels instead of codes, Yes or No for booleans, ISO dates, and empty strings for missing values; decimals stay numbers so spreadsheets can compute on them. `flatten_published_curation` gives a classification's columns (ID, absolute URL, version, published time in UTC, allele and CAR ID, haplotype name, disease, Mondo ID, IRI, classification as shown on the page, score, the taskforce fields named in `CLASSIFICATION_COLUMNS`, and the classification it updates). `flatten_evidence` gives an evidence record's columns (ID, score, publication, and the fields named in `EVIDENCE_COLUMNS`, with demographic groups joined by semicolons). `evidence_values` lists an evidence record's public column names and values for its HLArepo page, without the ID and publication columns and with decimals formatted. `flatten_classification_rows` joins them into one row per evidence record, giving a classification without evidence one row with blank evidence columns (`EVIDENCE_COLUMN_NAMES`). Haplotypes are represented by name alone, since the name lists the alleles.

### `tables.py`

Defines `PublishedCurationTable` (a `django-tables2` table) that renders the searchable list of published curations, with columns for ID, allele, haplotype, disease, classification (`Curation.classification_display`), published date, and per-row JSON, CSV, and Excel download buttons (`DOWNLOAD_BUTTONS`). There's no type column, since the filled-in allele or haplotype column shows it.

### `templates/repo/about.html`

Renders the HLArepo About page: what HLArepo is, how curations reach it from the HCI, and who maintains it.

### `templates/repo/acknowledgements.html`

Renders the HLArepo Acknowledgements page, crediting the NIH grant and contributors.

### `templates/repo/change.html`

Renders a single historical change record for a published curation, showing breadcrumbs back through the repo list, detail, and history pages, then including the shared `change_body.html` partial.

### `templates/repo/citing.html`

Renders the HLArepo Citing page with the citation format for HLArepo and a request to cite curation IDs and download dates.

### `templates/repo/collaborators.html`

Renders the HLArepo Collaborators page, listing partner organizations.

### `templates/repo/contact.html`

Renders the HLArepo Contact page with the maintainers' email address.

### `templates/repo/detail.html`

Renders the detail page for a published curation, including the superseded notice, the public summary partial, the family tree (`repo/partials/lineage.html`), the public evidence table (`repo/partials/evidence_table.html`), the `evidence-modal.js` script, and action buttons for JSON, CSV, and Excel downloads of that classification, history navigation, and (for curators) copying the curation for re-curation.

### `templates/repo/evidence.html`

Renders the public page for one evidence record of a published curation at `/repo/<curation>/evidence/<evidence>`, with breadcrumbs back through the detail page and the shared `repo/partials/evidence_body.html`. The evidence IDs on the detail page link here, and their eye icons load its body into the evidence modal.

### `templates/repo/partials/evidence_body.html`

An evidence record's publication with a PubMed linkout, its public values (`evidence_values`, the same labels and values as the CSV), and the scoring matrix (`evidence/partials/score.html`), wrapped in `#evidence-body` so HTMX can select it for the modal.

### `templates/repo/partials/evidence_modal.html`

The Bulma modal card that `evidence-modal.js` opens on the detail page. Its body is `#evidence-modal-body`, which HTMX fills with an evidence page's body.

### `templates/repo/partials/evidence_table.html`

The detail page's public evidence table, listing only the evidence in the `evidence` context variable (`public_evidence`): ID, publication with a PubMed linkout, score, and details. Each ID links to its evidence page. An eye icon in the Details column loads that page's body into the evidence modal with `hx-get` and `hx-select`, and `ignoreTitle` keeps the evidence page's title out of the browser tab. It includes the modal.

### `templates/repo/partials/lineage.html`

Renders the "Related Classifications" section: the family tree as a nested list, described by the plain-text description below it (`aria-describedby`). Shows nothing when there's no tree.

### `templates/repo/partials/lineage_node.html`

Renders one line of the family tree and, recursively, its updates. The box-drawing prefix is `aria-hidden`, since the nested list carries the structure. The current page is bold with `aria-current="page"` and a "You are here" tag; every other line links to its detail page. The newest gets a "Newest" tag.

### `templates/repo/partials/summary.html`

Renders the public summary of a published curation, without its ID, which the breadcrumb and title already show: the allele (or haplotype and each member allele) with ClinGen Allele Registry linkouts, the disease with a Mondo linkout, the classification (via `curation/partials/classification.html`), the score with linkouts to the scoring summary and the evidence scoring summary (`curation/scoring_summary.html` and `curation/evidence_scoring_summary.html`) that open in new tabs, the taskforce, the taskforce review date, the published date, the "Evidence Summary" heading and text, and, when set, the taskforce additional notes and the suggested classification override reason under smaller headings.

### `templates/repo/help.html`

Renders the HLArepo Help page, explaining how to report an issue by email.

### `templates/repo/history.html`

Renders the full audit-history page for a published curation, listing all historical records via the shared `history_body.html` partial with breadcrumbs linking back to the repo list and curation detail.

### `templates/repo/layouts/page.html`

The layout for the HLArepo info pages. It extends `layouts/public.html` and renders breadcrumbs rooted at HLArepo Home, a `heading` block, and a `content` block.

### `templates/repo/list.html`

Renders the HLArepo landing page at `/repo/`: the HCI logo, the HLArepo title and subtitle, a short description of HLArepo, a Downloads section with the bulk JSON, CSV, and Excel download buttons, and the searchable, paginated list of published curations (HTMX swaps in only the results partial).

### `tests.py`

Contains unit and integration tests covering the `PublishedCuration` model (creation, string representation, uniqueness constraint, reverse relation, `get_absolute_url`), publish and read-only enforcement views, the public detail page summary and linkouts, the public scoring summary pages, JSON download endpoints (including disease IRI and haplotype allele CAR IDs), supersession logic, and the curator "Copy and Recurate" button visibility.

### `urls.py`

Maps URL patterns for the repo app: the search/list page, the six info pages (About, Acknowledgements, Citing, Collaborators, Contact, Help), the bulk and single JSON, CSV, and XLSX download endpoints, and the curation detail, scoring summary, evidence scoring summary, evidence, history, and change views, all namespaced under the `repo-` prefix.

### `views.py`

Implements the repo views: `PublishedCurationList` (searchable table list, most recently published first), `PublishedCurationDetail` (with the public evidence list, supersession detection, and related-object prefetching for the linkouts), `PublishedScoringSummary` and `PublishedEvidenceScoringSummary` (a published curation's scoring summary and evidence scoring summary; 404 unless the curation is published), `PublishedEvidenceDetail` (one evidence record of a published curation, with its public values and the scoring framework; 404 unless the curation is published, owns the evidence, and includes it in the score), `PublishedCurationHistory` and `PublishedCurationChange` (history audit trail, with curator identities hidden: no Changed By column or row and no `published_by` diff), `download_all_json` / `download_single_json` function-based views that return indented JSON file attachments in one shared shape (export date, count, and a `curations` list), `download_all_csv` / `download_single_csv`, which return every published curation, or one, as a CSV attachment with one row per evidence record (newest first, UTF-8 with a byte order mark so Excel reads it correctly, with evidence prefetched to keep the query count constant), `download_all_xlsx` / `download_single_xlsx`, which return an Excel workbook with a Curations sheet (one row per curation) and an Evidence sheet (one row per evidence record, starting with its curation's ID), each with a bold, frozen header row, and both single downloads return 404 for a slug that isn't published, and function-based views for the six info pages.
