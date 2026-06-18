# `repo`

The `repo` app implements HLArepo, the public-facing repository of finalized HLA
curations. It provides the `PublishedCuration` model that links a completed curation to
a publication record, and exposes views for listing, viewing, and downloading published
curations as JSON. It also tracks the full change history of each published record via
`django-simple-history`.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `admin.py`

Registers `PublishedCuration` with the Django admin site using `SimpleHistoryAdmin`,
displaying the associated curation, publisher, publication timestamp, and version
number, with the publisher and timestamp fields set as read-only.

### `apps.py`

Defines the `RepoConfig` app configuration, setting `BigAutoField` as the default
primary key type and registering the app under the name `repo`.

### `models.py`

Defines the `PublishedCuration` model, which records a one-to-one relationship to a
`Curation`, the user who published it, the publication and update timestamps, and an
integer version number; full change history is tracked via `HistoricalRecords`.

### `serializers.py`

Provides `serialize_published_curation` and `serialize_evidence`, two plain functions
that convert a `PublishedCuration` instance and its associated `Evidence` records into
plain Python dictionaries suitable for JSON export.

### `templates/repo/change.html`

Displays the field-level diff for a single historical change to a published curation,
with a breadcrumb trail linking back to HLArepo, the curation detail page, and the
history list.

### `templates/repo/detail.html`

Shows the full details and evidence table for a single published curation, with buttons
to download the record as JSON and to view its change history.

### `templates/repo/history.html`

Lists all historical revisions for a published curation in a DataTables table, with each
row linking to the corresponding change-diff view.

### `templates/repo/list.html`

Renders a searchable DataTables table of all published curations, with columns for ID,
type, allele, haplotype, disease, classification, and last-updated date, plus a per-row
JSON download button and a bulk "Download All as JSON" button.

### `tests.py`

Contains unit and integration tests for the `PublishedCuration` model (creation, string
representation, one-to-one constraint, reverse relationship, `get_absolute_url`) and for
the publish, search, detail, JSON download, and read-only enforcement views.

### `urls.py`

Maps URL patterns for the repo app: the HLArepo list/search page, the bulk JSON download
endpoint, and per-curation detail, single JSON download, history, and change-diff views.

### `views.py`

Implements the `PublishedCurationList`, `PublishedCurationDetail`,
`PublishedCurationHistory`, and `PublishedCurationChange` class-based views, as well as
the `download_all_json` and `download_single_json` function-based views that return
serialized curation data as downloadable JSON attachments.
