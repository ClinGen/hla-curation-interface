# `src`

This directory contains the source code for the HLA Curation Interface (HCI), a Django
project for curating HLA alleles and haplotypes. It holds the Django project package
(`config`), the project's Django apps (`allele`, `auth_`, `common`, `core`, `curation`,
`disease`, `haplotype`, `publication`, `repo`), the shared static assets and site-wide
templates (`static`, `templates`), and the `manage.py` entry point used to run Django
commands.

### `manage.py`

Django's command-line entry point for administrative tasks. Loads environment variables
from the `.env` file via `python-dotenv` and then delegates to Django's
`execute_from_command_line`.

### `allele/`

Django app responsible for managing HLA alleles within the system, including creating
new allele records (with data fetched from the ClinGen Allele Registry), viewing allele
details, and listing alleles. See [`allele/README.md`](allele/README.md) for details.

### `auth_/`

Django app that handles user authentication and authorization, integrating with WorkOS
for hosted login and extending Django's built-in `User` model with an HCI-specific
`UserProfile`. The trailing underscore in the package name avoids a clash with Django's
bundled `auth` app. See [`auth_/README.md`](auth_/README.md) for details.

### `common/`

Django app that houses shared code and presentation pieces reused across the project's
other apps: a context processor for the current Git SHA, custom template filters,
reusable test mixins, and a library of small HTML template partials (icons, link outs,
form widgets, and status tags). See [`common/README.md`](common/README.md) for details.

### `config/`

Django project package. Defines the root URL configuration, the WSGI entry point used by
production servers, and the per-environment settings modules (`base`, `dev`, `prod`)
that wire up installed apps, middleware, templates, the database, static files,
authentication, and logging. See [`config/README.md`](config/README.md) for details.

### `core/`

Django app that provides the project's general-purpose, non-domain pages: the home page
(which links out to every search and create view in the system) and a small set of
informational pages (about, acknowledgements, citing, collaborators, contact, and help).
See [`core/README.md`](core/README.md) for details.

### `curation/`

Django app that is the core of the system. Lets curators create curations (for either an
allele or a haplotype, paired with a disease), attach `Evidence` records drawn from
publications, score that evidence against the HLA scoring framework, and publish "Done"
curations into the read-only repository. See [`curation/README.md`](curation/README.md)
for details.

### `disease/`

Django app that stores the diseases that curations are paired with. Each `Disease` is
identified by a Mondo Disease Ontology ID and is enriched with the name and IRI fetched
from the EBI Ontology Lookup Service. See [`disease/README.md`](disease/README.md) for
details.

### `haplotype/`

Django app that manages HLA haplotypes, sets of HLA alleles that travel together on the
same chromosome. A `Haplotype` is built from existing `Allele` records via a
many-to-many relationship, and its name is derived by sorting the constituent alleles by
gene location on chromosome 6. See [`haplotype/README.md`](haplotype/README.md) for
details.

### `publication/`

Django app that stores the publications that curations cite. Each `Publication` is
either a PubMed article, a bioRxiv preprint, or a medRxiv preprint, with metadata
fetched from PubMed's E-utilities API or the bioRxiv/medRxiv API. See
[`publication/README.md`](publication/README.md) for details.

### `repo/`

Django app that is the public-facing repository of finalized, published curations. Wraps
a `Curation` in a `PublishedCuration` record that snapshots the publication event
(publisher, timestamp, version) and exposes list, detail, and JSON download endpoints.
See [`repo/README.md`](repo/README.md) for details.

### `static/`

Static assets served by Django: vendored CSS and JavaScript libraries (Bulma, Bootstrap
Icons, Choices.js, htmx), project imagery (logos, favicons, third-party source logos),
web fonts, and the PWA web app manifest. See [`static/README.md`](static/README.md) for
details.

### `templates/`

Project-level Django templates: the shared base layout that every page extends, the
small partials that the layout pulls in (navbar, footer, flash messages,
account-activation banner), and the generic HTTP error pages (400, 403, 404, 500).
App-specific templates live under each Django app's own `templates/` subdirectory. See
[`templates/README.md`](templates/README.md) for details.
