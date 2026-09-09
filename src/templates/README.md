# `templates`

This directory contains the top-level Django templates shared across the entire application. It includes HTTP error pages, the base layout that all views extend, reusable UI partials included by that layout, and a custom django-tables2 rendering template. App-specific templates live in their respective app directories.

### `400.html`

Renders a 400 Bad Request error page, displayed when the server cannot process a malformed or invalid client request. Extends `layouts/base.html` and links back to the home page.

### `403.html`

Renders a 403 Forbidden error page with context-sensitive messaging based on the user's authentication and authorization state. It distinguishes between unauthenticated users, inactive accounts, users lacking curation permissions, and other general access denials.

### `404.html`

Renders a 404 Not Found error page when a requested URL does not match any known route. Extends `layouts/base.html` and links back to the home page.

### `500.html`

Renders a 500 Internal Server Error page when an unhandled server-side exception occurs. It instructs the user to try again and provides the support email address for persistent issues.

### `layouts/base.html`

The root layout template that all other page templates extend. It loads static assets (Bulma CSS, Bootstrap Icons, Choices.js, HTMX), sets up the `<head>` with favicon and meta blocks, and composes the page structure by including the environment banner, navbar, account activation notice, flash messages, and footer partials around a `{% block main %}` content slot.

### `partials/account_activation.html`

Displays an informational banner to authenticated users who have not yet completed account setup. It lists any outstanding steps — signing the PHI agreement or requesting curation permissions — along with a link to the HLA curation standard operating procedure.

### `partials/env_banner.html`

Shows a warning notification when the application is running in a non-production environment, alerting users that the site is a demo and that data will be periodically deleted.

### `partials/footer.html`

Renders the site-wide footer containing ClinGen and Stanford Medicine logos, navigation links (About, Contact, Citing, Help, Acknowledgements, Collaborators), copyright and funding attribution, a link to the open-source repository, and the current Git SHA.

### `partials/messages.html`

Iterates over Django's messages framework queue and renders each message as a dismissible Bulma notification styled by level (debug, info, success, warning, or error). Dismiss buttons use an HTMX inline event to remove the message block from the DOM without a page reload.

### `partials/navbar.html`

Renders the main navigation bar with dropdown menus for Alleles, Haplotypes, Diseases, Publications, and Curations (each offering Search and Add links). The right-hand side shows Log In or Log Out and Profile buttons depending on authentication state, plus a link to HLArepo. Includes a small script to enable the responsive burger menu toggle.

### `partials/navbar_link.html`

A micro-partial that renders a single `<a class="navbar-item">` link. It accepts `url` and `text` context variables and applies `has-text-weight-bold` when the link matches the currently active view.

### `tables.html`

A custom django-tables2 table template that wraps rendered tables in a horizontally scrollable container and replaces the default pagination controls with Bulma-styled previous/next buttons and a numbered page list. It also disables HTMX boosting on table rows to prevent unintended partial-page navigation.
