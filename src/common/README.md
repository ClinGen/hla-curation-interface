# `common`

This directory contains the `common` Django app for the HLA Curation Interface
(HCI). The app houses shared code and presentation pieces that are reused
across the project's other apps: a context processor that exposes the current
Git SHA to templates, custom template filters, reusable test mixins for
view-level tests, and a library of small HTML template partials (icons, link
outs, form widgets, and status tags) that other apps include from their own
templates.

### `__init__.py`

Marks the directory as a Python package.

### `context_processors.py`

Defines the `git_sha` context processor, which exposes `settings.GIT_SHA` to
templates as `GIT_SHA`.

### `templates/common/form/input/radio.html`

Renders a Bulma-styled radio input field with an optional hidden label, help
text, and field errors.

### `templates/common/form/input/text.html`

Renders a Bulma-styled text input field with an optional hidden label, help
text, configurable `type`, `autocomplete`, and `placeholder` attributes.

### `templates/common/form/select/default.html`

Renders a plain Bulma-styled `<select>` form field with an optional label,
help text, and additional CSS class.

### `templates/common/form/select/search.html`

Renders a searchable `<select>` form field, progressively enhanced on
`htmx:load` with the Choices.js library to support typeahead search and
removable selections.

### `templates/common/form/textarea.html`

Renders a Bulma-styled `<textarea>` form field with its label.

### `templates/common/icon.html`

Renders a Bootstrap Icons `<i>` element with a configurable icon name.

### `templates/common/linkout.html`

Renders an external link that opens in a new tab and is suffixed with a
box-arrow-up-right icon.

### `templates/common/tags/_generic.html`

Base partial for status tags; renders a Bulma `tag` with a configurable color,
icon, and text. The other tag partials wrap it with presets.

### `templates/common/tags/done.html`

Preset green "Done" status tag (uses `is-success` and the `check-circle-fill`
icon) used to indicate a completed item.

### `templates/common/tags/in_progress.html`

Preset yellow "In Progress" status tag (uses `is-warning` and the
`cone-striped` icon) used to indicate an item that is being worked on.

### `templates/common/tags/needs_review.html`

Preset red "Needs Review" status tag (uses `is-danger` and the `flag-fill`
icon) used to indicate an item that requires reviewer attention.

### `templates/common/tags/not_provided.html`

Preset yellow "Not Provided" status tag (uses `is-warning` and the
`check-circle` icon) used to indicate that an optional value is missing.

### `templates/common/tags/provided.html`

Preset green "Provided" status tag (uses `is-success` and the
`check-circle-fill` icon) used to indicate that an optional value is present.

### `templates/common/tags/published.html`

Preset light-blue "Published" status tag (uses `is-info is-light` and the
`book` icon) used to indicate publication state.

### `templatetags/__init__.py`

Marks the directory as a Python package so Django can register the template
tag library inside it.

### `templatetags/custom_filters.py`

Registers three template filters: `get_val` (read a model field by name),
`get_item` (read a dictionary value by key), and `in_get` (test whether a
value is present in `request.GET`).

### `tests.py`

Provides reusable test mixins for view tests: `BaseViewTestMixin` (template,
page name, and expected text assertions), `OpenViewTestMixin` (adds a
200-status check for anonymous users), and `ProtectedViewTestMixin` (sets up
four users with every combination of PHI-agreement and curation permissions
and asserts that only fully privileged users can access the view).
