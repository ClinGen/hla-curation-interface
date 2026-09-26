# `repo`

This Django app implements HLArepo, the public-facing repository of published HLA curations. It handles the `PublishedCuration` model (which wraps a completed `Curation`), exposes searchable list and detail views, tracks full change history via `django-simple-history`, and provides JSON download endpoints for individual or bulk export of published curation data.

### `__init__.py`

Empty file that marks `repo` as a Python package.

### `admin.py`

Registers `PublishedCuration` with the Django admin site using `SimpleHistoryAdmin`, displaying the associated curation, publisher, publication timestamp, and version in the list view.

### `apps.py`

Defines the `RepoConfig` app configuration, setting the app name to `repo` and the default auto field to `BigAutoField`.

### `models.py`

Defines the `PublishedCuration` model, which links one-to-one to a `Curation` and records who published it, when, and at what version. Change history is tracked automatically via `HistoricalRecords`.

### `serializers.py`

Provides `serialize_published_curation` and `serialize_evidence`, plain functions that convert `PublishedCuration` and `Evidence` instances to plain Python dictionaries suitable for JSON export, including all related entity, disease, and evidence fields. The export includes each allele's CAR ID (including haplotype member alleles) and the disease IRI.

### `tables.py`

Defines `PublishedCurationTable` (a `django-tables2` table) that renders the searchable list of published curations, with columns for ID, type, allele, haplotype, disease, classification, last-updated date, and a per-row JSON download button.

### `templates/repo/change.html`

Renders a single historical change record for a published curation, showing breadcrumbs back through the repo list, detail, and history pages, then including the shared `change_body.html` partial.

### `templates/repo/detail.html`

Renders the detail page for a published curation, including supersession and copied-from notices, the public summary partial, the evidence detail table, and action buttons for JSON download, history navigation, and (for curators) copying the curation for re-curation.

### `templates/repo/partials/summary.html`

Renders the public summary of a published curation: the curation ID, the allele (or haplotype and each member allele) with ClinGen Allele Registry linkouts, the disease with a Mondo linkout, the EP classification, the expert panel, the published date, and an "Evidence Summary" box. It deliberately omits the EP additional notes.

### `templates/repo/history.html`

Renders the full audit-history page for a published curation, listing all historical records via the shared `history_body.html` partial with breadcrumbs linking back to the repo list and curation detail.

### `templates/repo/list.html`

Renders the HLArepo search/list page, providing a search input, paginated results via HTMX partials, and a button to download all published curations as a single JSON file.

### `tests.py`

Contains unit and integration tests covering the `PublishedCuration` model (creation, string representation, uniqueness constraint, reverse relation, `get_absolute_url`), publish and read-only enforcement views, the public detail page summary and linkouts, JSON download endpoints (including disease IRI and haplotype allele CAR IDs), supersession logic, and the curator "Copy and Recurate" button visibility.

### `urls.py`

Maps URL patterns for the repo app: the search/list page, bulk and single JSON download endpoints, and the curation detail, history, and change views, all namespaced under the `repo-` prefix.

### `views.py`

Implements the repo views: `PublishedCurationList` (searchable table list), `PublishedCurationDetail` (with supersession detection and related-object prefetching for the linkouts), `PublishedCurationHistory` and `PublishedCurationChange` (history audit trail), and `download_all_json` / `download_single_json` function-based views that return serialized JSON responses as file attachments.
