# `templates`

This directory contains the application-wide Django templates: HTTP error pages, the
site-wide base layout, and reusable partials included across multiple views. These
templates are not tied to any single Django app and serve as the shared presentation
layer for the entire project.

### `400.html`

Renders a Bulma warning message box for HTTP 400 Bad Request errors, with a link back to
the home page.

### `403.html`

Renders a Bulma warning message box for HTTP 403 Forbidden errors, with context-aware
messaging that distinguishes between unauthenticated users, inactive accounts, users
lacking curation permissions, and all other cases.

### `404.html`

Renders a Bulma warning message box for HTTP 404 Not Found errors, with a link back to
the home page.

### `500.html`

Renders a Bulma danger message box for HTTP 500 Internal Server Error responses, with a
prompt to contact `hci@clinicalgenome.org` and a link back to the home page.

### `layouts/base.html`

The root HTML layout extended by all other page templates; loads all CSS and JS assets,
sets the CSRF token as an HTMX header, and composes the page by including the
environment banner, navbar, account activation notice, Django messages, main content
block, and footer partials.

### `partials/account_activation.html`

Displays an informational notice to authenticated users who have not yet signed the PHI
agreement or received curation permissions, with instructions and a link to request each
requirement.

### `partials/env_banner.html`

Shows a Bulma warning notification banner when the `ENV` setting is not `prod`, alerting
users that they are on a demo instance where data may be periodically deleted.

### `partials/footer.html`

Renders the site footer with logos and links for ClinGen and Stanford Medicine,
navigation links to About, Contact, Citing, Help, Acknowledgements, and Collaborators
pages, copyright text, NIH/NHGRI funding attribution, a link to the open-source
repository, and the current git SHA.

### `partials/messages.html`

Iterates over Django's message framework messages and renders each one as a dismissible
Bulma message component, with styling and an icon chosen based on the message tag
(debug, info, success, warning, or error).

### `partials/navbar.html`

Renders the main site navigation bar with dropdown menus for Alleles, Haplotypes,
Diseases, Publications, and Curations, plus Log In/Log Out, Profile, and HLArepo
buttons; also includes the JavaScript needed for the Bulma navbar-burger toggle on
mobile.

### `partials/navbar_link.html`

Renders a single `<a>` navbar item that applies a bold weight class when the link's URL
name matches the currently active view.
