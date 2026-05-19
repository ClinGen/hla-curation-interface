# `core`

This directory contains the `core` Django app for the HLA Curation Interface
(HCI). The app provides the project's general-purpose, non-domain pages: the
home page (which links out to every search and create view in the system and,
for authenticated users, lists the user's own curations) and a small set of
informational pages (about, acknowledgements, citing, collaborators, contact,
and help). The app has no models of its own; it consists of simple
function-based views that render static HTML templates.

### `__init__.py`

Marks the directory as a Python package.

### `apps.py`

Django `AppConfig` for the `core` app.

### `templates/core/about.html`

About page describing HCI as a tool for curating HLA alleles and haplotypes,
developed by the Stanford University contingent of the Clinical Genome Resource
project.

### `templates/core/acknowledgements.html`

Acknowledgements page crediting NIH U24 grant U24HG009649 and thanking Steven
Mack (Chair of the ClinGen HLA Working Group).

### `templates/core/citing.html`

Page describing how to cite the HCI, including the recommended citation format
and a note to also cite the specific dataset and download date when using HCI
data in research.

### `templates/core/collaborators.html`

Page listing the project's collaborators: the Baylor College of Medicine
ClinGen Team and ClinPGx.

### `templates/core/contact.html`

Contact page directing users to email `hci@clinicalgenome.org` to reach the
maintainers.

### `templates/core/help.html`

Help page linking to the HLA curation standard operating procedure and
explaining how to report issues via email, including the information users
should include in their report.

### `templates/core/home.html`

Home page. Shows a login status subtitle and a table of search and create links
for alleles, haplotypes, diseases, publications, and curations; for
authenticated users with curations, also renders the user's curations table.

### `templates/core/layouts/page.html`

Shared layout for the informational pages. Extends `layouts/base.html` and
exposes `heading` and `content` blocks so each page only needs to provide its
title, description, heading, and body.

### `tests.py`

Tests that each informational view returns 200 for anonymous users, uses the
expected template, and contains the expected page text (via `OpenViewTestMixin`
from `common.tests`). Also includes `AccountActivationMessageTest`, which sets
up four users covering every combination of PHI-agreement and curation
permissions and asserts that the home page shows the appropriate "missing PHI
agreement" and/or "no curation permissions" messages for each.

### `urls.py`

URL routes for the app: `home` (`""`), `about`, `acknowledgements`, `citing`,
`collaborators`, `contact`, and `help`.

### `views.py`

Function-based views (`home`, `about`, `contact`, `help_`, `citing`,
`acknowledgements`, `collaborators`) that each render the corresponding
template under `core/`.
