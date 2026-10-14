# `repo`

This Django app implements HLArepo, the public-facing repository of published HLA curations. Its pages extend `layouts/public.html`, which has no curator navigation or other links that need a login. It handles the `PublishedCuration` model (which wraps a completed `Curation`), exposes searchable list and detail views, tracks full change history via `django-simple-history`, and provides JSON download endpoints for individual or bulk export of published curation data.

### `__init__.py`

Empty file that marks `repo` as a Python package.

### `admin.py`

Registers `PublishedCuration` with the Django admin site using `SimpleHistoryAdmin`, displaying the associated curation, publisher, publication timestamp, and version in the list view.

### `apps.py`

Defines the `RepoConfig` app configuration, setting the app name to `repo` and the default auto field to `BigAutoField`.

### `constants.py`

Defines `PUBLIC_CURATION_FIELDS` and `PUBLIC_EVIDENCE_FIELDS`, the model fields shown in HLArepo and the JSON export. They're the single source of truth: the serializers build the export from them, and the forms mark these fields with a public badge. `needs_review` and every `*_notes` field on `Evidence` stay internal.

### `models.py`

Defines the `PublishedCuration` model, which links one-to-one to a `Curation` and records who published it, when, and at what version. Change history is tracked automatically via `HistoricalRecords`.

### `serializers.py`

Provides `serialize_published_curation` and `serialize_evidence`, plain functions that convert `PublishedCuration` and `Evidence` instances to plain Python dictionaries suitable for JSON export. The taskforce and evidence data fields come from the public field lists in `constants.py`; `EXPORT_NAMES` keeps the `classification` key for `taskforce_classification`. The export includes each allele's CAR ID (including haplotype member alleles), the disease IRI, the taskforce override reason, and the taskforce review date as an ISO date or `null`. It also builds rows for flat files, with readable column names and readable values: choice labels instead of codes, Yes or No for booleans, ISO dates, and empty strings for missing values; decimals stay numbers so spreadsheets can compute on them. `flatten_published_curation` gives a classification's columns (ID, absolute URL, version, published time in UTC, allele and CAR ID, haplotype name, disease, Mondo ID, IRI, classification as shown on the page, score, the taskforce fields named in `CLASSIFICATION_COLUMNS`, and the classification it updates). `flatten_evidence` gives an evidence record's columns (ID, whether it's included, score, publication, and the fields named in `EVIDENCE_COLUMNS`, with demographic groups joined by semicolons). `flatten_classification_rows` joins them into one row per evidence record, giving a classification without evidence one row with blank evidence columns (`EVIDENCE_COLUMN_NAMES`). Haplotypes are represented by name alone, since the name lists the alleles.

### `tables.py`

Defines `PublishedCurationTable` (a `django-tables2` table) that renders the searchable list of published curations, with columns for ID, allele, haplotype, disease, classification (`Curation.classification_display`), published date, and a per-row JSON download button. There's no type column, since the filled-in allele or haplotype column shows it.

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

Renders the detail page for a published curation, including supersession and copied-from notices, the public summary partial, the evidence detail table (with `public=True`, so evidence IDs don't link to curator pages), and action buttons for JSON download, history navigation, and (for curators) copying the curation for re-curation.

### `templates/repo/partials/summary.html`

Renders the public summary of a published curation: the curation ID, the allele (or haplotype and each member allele) with ClinGen Allele Registry linkouts, the disease with a Mondo linkout, the classification (via `curation/partials/classification.html`), the taskforce, the taskforce review date, the published date, the "Evidence Summary" heading and text, and the taskforce additional notes and, when set, the override reason under smaller headings.

### `templates/repo/help.html`

Renders the HLArepo Help page, explaining how to report an issue by email.

### `templates/repo/history.html`

Renders the full audit-history page for a published curation, listing all historical records via the shared `history_body.html` partial with breadcrumbs linking back to the repo list and curation detail.

### `templates/repo/layouts/page.html`

The layout for the HLArepo info pages. It extends `layouts/public.html` and renders breadcrumbs rooted at HLArepo Home, a `heading` block, and a `content` block.

### `templates/repo/list.html`

Renders the HLArepo landing page at `/repo/`: the HCI logo, the HLArepo title and subtitle, a short description of HLArepo, a Downloads section with the bulk JSON and CSV download buttons, and the searchable, paginated list of published curations (HTMX swaps in only the results partial).

### `tests.py`

Contains unit and integration tests covering the `PublishedCuration` model (creation, string representation, uniqueness constraint, reverse relation, `get_absolute_url`), publish and read-only enforcement views, the public detail page summary and linkouts, JSON download endpoints (including disease IRI and haplotype allele CAR IDs), supersession logic, and the curator "Copy and Recurate" button visibility.

### `urls.py`

Maps URL patterns for the repo app: the search/list page, the six info pages (About, Acknowledgements, Citing, Collaborators, Contact, Help), the bulk JSON and CSV and single JSON download endpoints, and the curation detail, history, and change views, all namespaced under the `repo-` prefix.

### `views.py`

Implements the repo views: `PublishedCurationList` (searchable table list, most recently published first), `PublishedCurationDetail` (with supersession detection and related-object prefetching for the linkouts), `PublishedCurationHistory` and `PublishedCurationChange` (history audit trail), `download_all_json` / `download_single_json` function-based views that return serialized JSON responses as file attachments, `download_all_csv`, which streams every published classification as a CSV attachment with one row per evidence record (newest classification first, UTF-8 with a byte order mark so Excel reads it correctly, with evidence prefetched to keep the query count constant), and function-based views for the six info pages.
