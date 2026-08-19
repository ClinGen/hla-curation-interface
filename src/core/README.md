# `core`

The `core` app provides the top-level informational pages of the HLA Curation Interface:
home, about, contact, help, citing, acknowledgements, and collaborators. It also serves
as the Django app that owns the root URL configuration and the shared
`layouts/page.html` template shell used by all of those pages. It has no models of its
own.

### `__init__.py`

Empty file marking `core` as a Python package.

### `apps.py`

Defines `CoreConfig`, the Django `AppConfig` for the `core` app, registering it under
the name `"core"` with `BigAutoField` as the default primary key type.

### `templates/core/about.html`

Renders the About page. Extends `core/layouts/page.html` and displays a short paragraph
describing the HLA Curation Interface and its development by Stanford University's
ClinGen contingent.

### `templates/core/acknowledgements.html`

Renders the Acknowledgements page. Credits NIH U24 grant U24HG009649 as the funding
source and thanks Steven Mack (UCSF, Chair of the ClinGen HLA Working Group) for his
contributions.

### `templates/core/citing.html`

Renders the Citing page. Provides a recommended citation format for the HCI and
instructs users to also cite the specific dataset and download date when using HCI data
in research.

### `templates/core/collaborators.html`

Renders the Collaborators page. Lists external collaborating organizations — the Baylor
College of Medicine ClinGen Team and ClinPGx — as a linked bullet list.

### `templates/core/contact.html`

Renders the Contact page. Displays a mailto link to `hci@clinicalgenome.org` for
reaching HCI maintainers.

### `templates/core/help.html`

Renders the Help page. Links to the HLA curation standard operating procedure (Google
Doc) and provides email instructions for reporting issues, including what information to
include (description, reproduction steps, OS, browser, screenshots).

### `templates/core/home.html`

Renders the Home page. Shows the authenticated user's email (or "not logged in"), a
navigation table with search and create links for alleles, haplotypes, diseases,
publications, and curations, and — for authenticated users — a `django-tables2` table of
that user's own curations.

### `templates/core/layouts/page.html`

A shared layout template that extends `layouts/base.html`. It wraps content in a Bulma
`.box`, renders a breadcrumb nav with a Home link and an active page entry (populated
via the `heading` block), and provides a `content` block for page-specific body content.

### `tests.py`

Contains `OpenViewTestMixin`-based tests for each of the seven core views
(`HomeViewTest`, `AboutViewTest`, `ContactViewTest`, `HelpViewTest`, `CitingViewTest`,
`AcknowledgementsViewTest`, `CollaboratorsViewTest`) that verify HTTP 200 responses and
expected page text. Also contains `AccountActivationMessageTest`, which tests all four
combinations of PHI agreement and curation permission status to verify the correct
warning messages appear (or don't appear) on the home page.

### `urls.py`

Defines URL patterns for all seven core views, mapping bare paths (`""`, `"about"`,
`"acknowledgements"`, `"citing"`, `"collaborators"`, `"contact"`, `"help"`) to their
respective view functions.

### `views.py`

Defines simple function-based views for each core page. The `home` view additionally
builds a `CurationTable` (via `django-tables2`) of the authenticated user's curations
and passes it to the template. All other views are thin wrappers around `render`.
