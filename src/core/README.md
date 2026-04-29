# Core

This directory contains the `core` Django app for the HLA Curation Interface
(HCI). The app provides the project's general-purpose, non-domain pages: the
home page (which links out to every search and create view in the system and,
for authenticated users, lists the user's own curations) and a small set of
informational pages (about, acknowledgements, citing, collaborators, contact,
and help). The app has no models of its own; it consists of simple
function-based views that render static HTML templates.

## Files

- `__init__.py` — Marks the directory as a Python package.
- `apps.py` — Django `AppConfig` for the `core` app.
- `tests.py` — Tests that each informational view returns 200 for anonymous
  users, uses the expected template, and contains the expected page text
  (via `OpenViewTestMixin` from `common.tests`). Also includes
  `AccountActivationMessageTest`, which sets up four users covering every
  combination of PHI-agreement and curation permissions and asserts that the
  home page shows the appropriate "missing PHI agreement" and/or "no curation
  permissions" messages for each.
- `urls.py` — URL routes for the app: `home` (`""`), `about`, `citing`,
  `acknowledgements`, `collaborators`, `contact`, and `help`.
- `views.py` — Function-based views (`home`, `about`, `contact`, `help_`,
  `citing`, `acknowledgements`, `collaborators`) that each render the
  corresponding template under `core/`.

## Subdirectories

- `templates/core/` — HTML templates for the app:
  - `home.html` — Home page. Shows a login status subtitle and a table of
    search/create links for alleles, haplotypes, diseases, publications, and
    curations; for authenticated users with curations, also renders the
    user's curations table.
  - `about.html` — About page describing HCI and its maintainers.
  - `acknowledgements.html` — Acknowledgements page (e.g., NIH/NHGRI funding,
    Steven Mack).
  - `citing.html` — Page describing how to cite HCI and its dataset.
  - `collaborators.html` — Page listing collaborating teams (e.g., the Baylor
    College of Medicine ClinGen Team, ClinPGx).
  - `contact.html` — Contact page with the `hci@clinicalgenome.org` email
    address.
  - `help.html` — Help page pointing users at the standard operating procedure
    and the contact email.
  - `layouts/page.html` — Shared layout for the informational pages. Extends
    `layouts/base.html` and exposes `heading` and `content` blocks so each
    page only needs to provide its title, description, heading, and body.
