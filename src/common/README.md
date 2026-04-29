# Common

This directory contains the `common` Django app for the HLA Curation Interface
(HCI). The app houses shared code and presentation pieces that are reused
across the project's other apps: a context processor that exposes the current
Git SHA to templates, custom template filters, reusable test mixins for
view-level tests, and a library of small HTML template partials (icons, link
outs, form widgets, and status tags) that other apps include from their own
templates.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `context_processors.py` — Defines the `git_sha` context processor, which
  exposes `settings.GIT_SHA` to templates as `GIT_SHA`.
- `tests.py` — Provides reusable test mixins for view tests: `BaseViewTestMixin`
  (template, page name, and expected text assertions), `OpenViewTestMixin` (adds
  a 200-status check for anonymous users), and `ProtectedViewTestMixin` (sets
  up four users with every combination of PHI-agreement and curation
  permissions and asserts that only fully privileged users can access the
  view).

## Subdirectories

- `templatetags/` — Custom Django template tag library. `custom_filters.py`
  registers three filters: `get_val` (read a model field by name), `get_item`
  (read a dictionary value by key), and `in_get` (test whether a value is
  present in `request.GET`).
- `templates/common/` — Reusable HTML template partials included by other
  apps:
  - `icon.html` — Renders a Bootstrap Icons `<i>` element with a configurable
    icon name.
  - `linkout.html` — Renders an external link that opens in a new tab with a
    box-arrow-up-right icon.
  - `form/textarea.html` — Renders a Bulma-styled `<textarea>` form field.
  - `form/input/radio.html`, `form/input/text.html` — Radio and text input
    widgets.
  - `form/select/default.html`, `form/select/search.html` — Plain and
    searchable select widgets.
  - `tags/_generic.html` — Base partial for status tags; the other tag
    partials wrap it with preset color, icon, and text.
  - `tags/done.html`, `tags/in_progress.html`, `tags/needs_review.html`,
    `tags/not_provided.html`, `tags/provided.html`, `tags/published.html` —
    Preset status tags used to indicate curation and publication state.
