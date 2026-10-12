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

### `templates/common/confirm_modal.html`

The Bulma modal card that `hci/js/confirm-modal.js` shows before submitting a form with a `data-confirm` attribute. `layouts/base.html` includes it once on every page.


### `templates/common/form/input/radio.html`

Reusable partial for rendering a radio-button form field using Bulma CSS. Supports optional label hiding and help-text display. Pass `public=True` to mark the field as shown in HLArepo: the badge sits in the label. A hidden label gets no badge, so put it on the section heading (`section_heading.html`) instead.

### `templates/common/form/input/text.html`

Reusable partial for rendering a text `<input>` form field using Bulma CSS. Accepts context variables for `type`, `autocomplete`, and `placeholder`, and supports optional label hiding and help-text display. Pass `public=True` to mark the field as shown in HLArepo: the badge sits in the label. A hidden label gets no badge, so put it on the section heading (`section_heading.html`) instead.

### `templates/common/form/section_heading.html`

A form section's `<h2>` heading. Callers pass `id`, `text`, and `public`; when `public` is true, the public badge sits next to the heading text. The evidence edit form uses it because its field labels are hidden, so the badge can't go next to them.

### `templates/common/form/select/default.html`

Reusable partial for rendering a standard `<select>` form field using Bulma CSS. Supports optional label visibility, help text, and an extra CSS class on the select wrapper. Pass `public=True` to mark the field as shown in HLArepo: the badge sits in the label. A hidden label gets no badge, so put it on the section heading (`section_heading.html`) instead.

### `templates/common/form/select/search.html`

Reusable partial for rendering a `<select>` field enhanced with the Choices.js library for fuzzy search. Initialises the Choices widget on HTMX load with configurable fuse search options and a remove-item button. Pass `public=True` to mark the field as shown in HLArepo: the badge sits in the label. A hidden label gets no badge, so put it on the section heading (`section_heading.html`) instead.

### `templates/common/form/textarea.html`

Reusable partial for rendering a `<textarea>` form field using Bulma CSS, with a visible label, inline validation errors, and optional help text. Pass `public=True` to put the public badge in the label.

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

### `templates/common/public_badge.html`

A globe icon marking a form field that's shown publicly in HLArepo. It uses `common/tooltip.html` with the text "This will be visible in the public-facing HLArepo once published."

### `templates/common/tooltip.html`

An icon with a Tippy.js tooltip and no visible text. Callers pass `icon_name`, `text`, and optional `classes`. The icon is keyboard-focusable, and the text is also in an `is-sr-only` span for screen readers. `hci/js/tooltips.js` attaches the tooltip.

### `templates/common/tags/_generic.html`

Base tag partial that renders a light Bulma `<span class="tag">` with a given `color`, `icon_name`, and `text`. All concrete tag templates include this partial via `{% include %}` with specific values.

### `templates/common/tags/approved.html`

Renders a green "Approved" curation status tag using `_generic.html` with a check-circle icon.

### `templates/common/tags/done.html`

Renders a green "Done" status tag using `_generic.html` with a filled check-circle icon.

### `templates/common/tags/in_progress.html`

Renders a grey "In Progress" status tag using `_generic.html` with a cone-striped icon.

### `templates/common/tags/needs_review.html`

Renders a red "Needs Review" status tag using `_generic.html` with a filled flag icon.

### `templates/common/tags/not_provided.html`

Renders a grey "Not Provided" status tag using `_generic.html` with an outline check-circle icon.

### `templates/common/tags/provided.html`

Renders a green "Provided" status tag using `_generic.html` with a filled check-circle icon.

### `templates/common/tags/provisional.html`

Renders a yellow "Provisional" curation status tag using `_generic.html` with an hourglass icon. Provisional curations are waiting on the expert panel.

### `templates/common/tags/published.html`

Renders a blue "Published" status tag using `_generic.html` with a book icon.

### `templatetags/__init__.py`

Empty file that marks `templatetags` as a Python package, enabling Django to discover the custom template filters defined in this directory.

### `templatetags/custom_filters.py`

Registers four custom Django template filters: `get_val` (retrieves a named attribute from a model instance), `get_item` (retrieves a key from a dictionary), `in_get` (checks whether a string is present in `request.GET`), and `is_public` (checks a curation or evidence field name against the lists in `repo/constants.py`, dropping the `_string` suffix that some evidence form fields use).

### `tests.py`

Provides reusable test mixins (`OpenViewTestMixin`, `ProtectedViewTestMixin`, `SuppressRequestLoggingMixin`) that enforce standard view-test contracts across the project, along with `IsPublicFilterTest`, `PublicBadgeTooltipTest`, which checks the globe badge's tooltip and that no text sits beside it, `ColorKeyTest`, which checks tags, buttons (in templates and `tables.py` files), and the EP feedback panel against the color key in `docs/design.md`, the `field_block` helper for checking a field's public badge, `MigrationsUpToDateTest`, which fails when a model change has no migration, and `SearchListViewTest`, which exercises the search and HTMX partial-response behaviour of `SearchListView`.

### `views.py`

Defines `SearchListView`, a `ListView` subclass that adds case-insensitive multi-field search via a `q` GET parameter, returns only the `search_results` partial when the request carries an `HX-Request` header, and injects `query` and `result_count` into the template context.
