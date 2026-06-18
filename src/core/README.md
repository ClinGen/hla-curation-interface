# `core`

The `core` app provides the application shell: the home page, static informational pages
(About, Acknowledgements, Citing, Collaborators, Contact, Help), the shared page layout
template, and the views and URL routes that serve them. It does not define any database
models.

### `__init__.py`

Empty file; marks this directory as a Python package.

### `apps.py`

Django `AppConfig` for the `core` app; sets the default auto field to `BigAutoField` and
registers the app under the name `core`.

### `templates/core/about.html`

Renders the About page, which briefly describes the HLA Curation Interface and its
development by the Stanford University ClinGen team.

### `templates/core/acknowledgements.html`

Renders the Acknowledgements page, crediting NIH U24 grant U24HG009649 and thanking
Steven Mack (Chair of the ClinGen HLA Working Group).

### `templates/core/citing.html`

Renders the Citing page, providing the recommended citation format for the HCI and a
note about citing specific datasets.

### `templates/core/collaborators.html`

Renders the Collaborators page, listing the Baylor College of Medicine ClinGen Team and
ClinPGx as collaborators.

### `templates/core/contact.html`

Renders the Contact page, directing users to email `hci@clinicalgenome.org` to reach the
maintainers.

### `templates/core/help.html`

Renders the Help page, linking to the standard operating procedure document and
providing instructions for reporting issues via email.

### `templates/core/home.html`

Renders the Home page, displaying a navigation table with links to create and search
alleles, haplotypes, diseases, publications, and curations, and showing the current
user's own curations if they are logged in.

### `templates/core/layouts/page.html`

A simple layout template that extends the base layout and defines `heading` and
`content` blocks used by the informational pages (About, Contact, Help, etc.).

### `tests.py`

Contains Django `TestCase` classes that verify each informational page returns HTTP 200,
uses the correct template, and contains expected text, and an
`AccountActivationMessageTest` that checks the home page shows or hides PHI agreement
and curation permission warning messages based on the user's profile state.

### `urls.py`

Maps URL paths to core views: the root path (`""`) to `home`, plus named routes for
`about`, `acknowledgements`, `citing`, `collaborators`, `contact`, and `help`.

### `views.py`

Defines one simple function-based view per page (`home`, `about`, `contact`, `help_`,
`citing`, `acknowledgements`, `collaborators`), each of which renders its corresponding
template.
