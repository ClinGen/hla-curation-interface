# `common`

This Django app provides shared utilities, base classes, and reusable UI components used across the rest of the project. It includes context processors, history diffing helpers, a generic search-enabled list view, custom template filters, and a library of reusable templates for form fields, status tags, history display, and search partials. Nothing in this app is domain-specific; it exists to keep cross-cutting concerns in one place.

### `__init__.py`

Empty file that marks `common` as a Python package.

### `context_processors.py`

Provides two Django context processors — `git_sha` and `env` — that inject the current Git SHA and environment name into every template context.

### `history.py`

Provides `resolve_changes`, which computes a human-readable diff between two django-simple-history records. It maps internal field names to their `verbose_name` labels and resolves choice values to their display strings.

### `tables.py`

Defines `HistoryTable`, a django-tables2 `Table` subclass for rendering an object's audit history. It renders the change type as a labelled icon link pointing to the corresponding change-detail view.

### `templates/common/form/input/radio.html`

Reusable partial for rendering a radio-button form field using Bulma CSS. Supports optional label hiding and help-text display.

### `templates/common/form/input/text.html`

Reusable partial for rendering a text `<input>` form field using Bulma CSS. Accepts context variables for `type`, `autocomplete`, and `placeholder`, and supports optional label hiding and help-text display.

### `templates/common/form/select/default.html`

Reusable partial for rendering a standard `<select>` form field using Bulma CSS. Supports optional label visibility, help text, and an extra CSS class on the select wrapper.

### `templates/common/form/select/search.html`

Reusable partial for rendering a `<select>` field enhanced with the Choices.js library for fuzzy search. Initialises the Choices widget on HTMX load with configurable fuse search options and a remove-item button.

### `templates/common/form/textarea.html`

Reusable partial for rendering a `<textarea>` form field using Bulma CSS, with a visible label, inline validation errors, and optional help text.

### `templates/common/history/change_body.html`

Renders the detail view for a single history record: a metadata table (changed-by, change type, date) and, for update records, a before/after diff table of individual field changes.

### `templates/common/history/history_body.html`

Renders the full audit-history table for an object using django-tables2's `render_table` tag inside a scrollable container.

### `templates/common/icon.html`

Renders a single Bootstrap Icons `<i>` element given an `icon_name` context variable.

### `templates/common/linkout.html`

Renders an external anchor tag that opens in a new tab, appending a Bootstrap Icons "box-arrow-up-right" icon to signal the external destination.

### `templates/common/partials/search_input.html`

Renders the live-search text input used on list pages. Uses HTMX to fire a GET request to the current path on keyup (with a 500 ms debounce) and swap the result into `#search-results`, pushing the updated URL.

### `templates/common/partials/search_results.html`

Renders the result count and, when results exist, the django-tables2 table inside an HTMX-boosted container targeting `#search-results`. Used as the HTMX partial response for search queries.

### `templates/common/tags/_generic.html`

Base tag partial that renders a Bulma `<span class="tag">` with a given `color`, `icon_name`, and `text`. All concrete tag templates include this partial via `{% include %}` with specific values.

### `templates/common/tags/done.html`

Renders a green "Done" status tag using `_generic.html` with a filled check-circle icon.

### `templates/common/tags/in_progress.html`

Renders a yellow "In Progress" status tag using `_generic.html` with a cone-striped icon.

### `templates/common/tags/needs_review.html`

Renders a red "Needs Review" status tag using `_generic.html` with a filled flag icon.

### `templates/common/tags/not_provided.html`

Renders a yellow "Not Provided" status tag using `_generic.html` with an outline check-circle icon.

### `templates/common/tags/provided.html`

Renders a green "Provided" status tag using `_generic.html` with a filled check-circle icon.

### `templates/common/tags/published.html`

Renders a light-blue "Published" status tag using `_generic.html` with a book icon.

### `templatetags/__init__.py`

Empty file that marks `templatetags` as a Python package, enabling Django to discover the custom template filters defined in this directory.

### `templatetags/custom_filters.py`

Registers three custom Django template filters: `get_val` (retrieves a named attribute from a model instance), `get_item` (retrieves a key from a dictionary), and `in_get` (checks whether a string is present in `request.GET`).

### `tests.py`

Provides reusable test mixins (`OpenViewTestMixin`, `ProtectedViewTestMixin`, `SuppressRequestLoggingMixin`) that enforce standard view-test contracts across the project, along with `SearchListViewTest`, which exercises the search and HTMX partial-response behaviour of `SearchListView`.

### `views.py`

Defines `SearchListView`, a `ListView` subclass that adds case-insensitive multi-field search via a `q` GET parameter, returns only the `search_results` partial when the request carries an `HX-Request` header, and injects `query` and `result_count` into the template context.
