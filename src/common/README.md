# `common`

The `common` app provides shared utilities, template partials, and test helpers used
across the rest of the HCI. It includes a context processor for injecting environment
metadata, a utility for generating human-readable history diffs, a library of reusable
form and tag templates, and base test mixins that encode the application's standard
access-control assumptions.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `context_processors.py`

Defines two context processors — `git_sha` and `env` — that inject the current Git SHA
and environment name (from Django settings) into every template context.

### `history.py`

Defines `resolve_changes`, which compares two `django-simple-history` records and
returns a list of field-level diffs with human-readable field labels and choice display
values. Returns `None` when there is no previous record (i.e. the record represents a
creation event).

### `templates/common/form/input/radio.html`

A reusable partial that renders a labeled group of radio button inputs for a form field,
with optional help text and validation errors styled with Bulma CSS classes.

### `templates/common/form/input/text.html`

A reusable partial that renders a labeled Bulma text input for a form field, supporting
optional help text, validation errors, `type`, `autocomplete`, and `placeholder`
attributes.

### `templates/common/form/select/default.html`

A reusable partial that renders a labeled Bulma `<select>` dropdown for a form field,
with optional help text, validation errors, and an optional additional CSS class on the
wrapper element.

### `templates/common/form/select/search.html`

A reusable partial that renders a labeled select field enhanced with the Choices.js
library for client-side search, remove-item, and no-results feedback, initialized on
`htmx:load`.

### `templates/common/form/textarea.html`

A reusable partial that renders a labeled textarea for a form field using Bulma's
field/control structure.

### `templates/common/history/change_body.html`

A reusable partial that renders the body of a change detail page, showing who made the
change, the change type (Created / Updated / Deleted), and the date, followed by a
field-level before/after diff table when the change type is an update.

### `templates/common/history/history_body.html`

A reusable partial that renders a DataTables-powered table of history records (Changed
By, Change type with icon, Date), building the per-record URL dynamically from up to two
slug arguments passed via template context.

### `templates/common/icon.html`

A one-line partial that renders a Bootstrap Icons `<i>` element for a given `icon_name`.

### `templates/common/linkout.html`

A reusable partial that renders an external hyperlink that opens in a new tab, appending
a Bootstrap Icons "box arrow up right" icon to indicate it leaves the site.

### `templates/common/tags/_generic.html`

The base partial for all status tag partials; renders a Bulma `tag` `<span>` with a
given color, Bootstrap icon, and text.

### `templates/common/tags/done.html`

Renders a green "Done" status tag by including `_generic.html` with `is-success` color
and a filled check-circle icon.

### `templates/common/tags/in_progress.html`

Renders a yellow "In Progress" status tag by including `_generic.html` with `is-warning`
color and a cone-striped icon.

### `templates/common/tags/needs_review.html`

Renders a red "Needs Review" status tag by including `_generic.html` with `is-danger`
color and a filled flag icon.

### `templates/common/tags/not_provided.html`

Renders a yellow "Not Provided" status tag by including `_generic.html` with
`is-warning` color and an outline check-circle icon.

### `templates/common/tags/provided.html`

Renders a green "Provided" status tag by including `_generic.html` with `is-success`
color and a filled check-circle icon.

### `templates/common/tags/published.html`

Renders a light-blue "Published" status tag by including `_generic.html` with
`is-info is-light` color and a book icon.

### `templatetags/__init__.py`

Empty file; marks this directory as a Python package.

### `templatetags/custom_filters.py`

Registers three custom Django template filters: `get_val` (retrieves a named attribute
from a model instance), `get_item` (retrieves a value from a dictionary by key), and
`in_get` (checks whether a string is present as a key in `request.GET`).

### `tests.py`

Provides `BaseViewTestMixin`, `OpenViewTestMixin`, and `ProtectedViewTestMixin` —
reusable test mixins imported by other apps' test suites. `ProtectedViewTestMixin`
creates four users covering all combinations of PHI-agreement and curation-permission
flags and asserts that only the user with both flags set can access a protected view.
