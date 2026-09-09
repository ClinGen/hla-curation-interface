# `core`

The `core` Django app serves as the top-level application for the HLA Curation Interface, providing the home page and a set of static informational pages (About, Contact, Help, Citing, Acknowledgements, Collaborators). It defines the URL routing for these pages, their corresponding views, and the shared page layout template that all informational pages inherit from.

### `__init__.py`

Empty file that marks `core` as a Python package.

### `apps.py`

Defines `CoreConfig`, the Django `AppConfig` subclass that registers the `core` app with `default_auto_field` set to `BigAutoField`.

### `templates/core/about.html`

Renders the About page, which briefly describes the HLA Curation Interface as a tool for curating HLA allele and haplotype information developed by the Stanford University ClinGen team.

### `templates/core/acknowledgements.html`

Renders the Acknowledgements page, crediting the NIH/NHGRI U24 grant (U24HG009649) and thanking contributors such as Steven Mack, Chair of the ClinGen HLA Working Group.

### `templates/core/citing.html`

Renders the Citing page, providing a recommended citation format for the HCI and instructing users to also cite the specific dataset and download date when referencing HCI data in research.

### `templates/core/collaborators.html`

Renders the Collaborators page, listing external collaborating organizations including the Baylor College of Medicine ClinGen Team and ClinPGx.

### `templates/core/contact.html`

Renders the Contact page, directing users to reach the HCI maintainers at `hci@clinicalgenome.org`.

### `templates/core/help.html`

Renders the Help page, linking to the HLA curation standard operating procedure and providing instructions for reporting issues (including what information to include in a bug report email).

### `templates/core/home.html`

Renders the home page, displaying the user's login status, navigation links for searching and adding alleles, haplotypes, diseases, publications, and curations, and a table of the authenticated user's own curations.

### `templates/core/layouts/page.html`

A shared layout template for all informational pages that extends the base layout, rendering a breadcrumb nav (linking back to Home), a page heading block, and a content block inside a box container.

### `tests.py`

Contains view tests for each core page (Home, About, Contact, Help, Citing, Acknowledgements, Collaborators) using `OpenViewTestMixin`, and an `AccountActivationMessageTest` that verifies the correct PHI agreement and curation-permission warning messages are shown to users in each combination of account activation states.

### `urls.py`

Maps URL paths to core views: the root path to `home`, and named paths for `about`, `acknowledgements`, `citing`, `collaborators`, `contact`, and `help`.

### `views.py`

Defines one function-based view per core page. The `home` view additionally queries the authenticated user's curations and passes a `CurationTable` to the template; all other views simply render their corresponding template.
