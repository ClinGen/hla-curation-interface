# `templates`

This directory contains the top-level Django templates shared across the entire application. It includes HTTP error pages, the curator layout (`layouts/base.html`), the public HLArepo layout (`layouts/public.html`), reusable UI partials included by those layouts, and a custom django-tables2 rendering template. App-specific templates live in their respective app directories.

### `400.html`

Renders a 400 Bad Request error page, displayed when the server cannot process a malformed or invalid client request. Extends `layouts/base.html` and links back to the home page.

### `403.html`

Renders a 403 Forbidden error page with context-sensitive messaging based on the user's authentication and authorization state. It distinguishes between unauthenticated users, inactive accounts, users lacking curation permissions, and other general access denials.

### `404.html`

Renders a 404 Not Found error page when a requested URL does not match any known route. Extends `layouts/base.html` and links back to the home page.

### `500.html`

Renders a 500 Internal Server Error page when an unhandled server-side exception occurs. It instructs the user to try again and provides the support email address for persistent issues.

### `layouts/base.html`

The curator layout that every HCI page extends. It loads static assets (Bulma CSS, Bootstrap Icons, Choices.js, HTMX, Tippy.js and Popper, the tooltip script, and the confirm modal script), sets up the `<head>` with favicon and meta blocks, and composes the page structure by including the environment banner, navbar, account activation notice, flash messages, and footer partials around a `{% block main %}` content slot, followed by the shared confirm modal (`common/confirm_modal.html`).

### `layouts/public.html`

The public layout that HLArepo pages extend. It loads the same assets as `layouts/base.html` minus Choices.js, which no public page uses, and its title prefix is "HLArepo". It includes the environment banner, the public navbar, flash messages, the public footer, and the confirm modal, but not the curator navbar or the account activation notice, so a visitor never sees a link that needs a login.

### `partials/account_activation.html`

Displays an informational banner to authenticated users who have not yet completed account setup. It lists any outstanding steps: signing the PHI agreement or requesting curation permissions.

### `partials/env_banner.html`

Shows a warning notification when the application is running in a non-production environment, alerting users that the site is a demo and that data will be periodically deleted.

### `partials/footer.html`

Renders the HCI footer containing the ClinGen and Stanford Medicine logos (from `footer_logos.html`), navigation links (About, Contact, Citing, Help, Acknowledgements, Collaborators), copyright and funding attribution, a link to the open-source repository, and the current Git SHA.

### `partials/footer_logos.html`

Renders the ClinGen and Stanford Medicine logo columns. Both footers include it so their logos don't drift apart.

### `partials/messages.html`

Iterates over Django's messages framework queue and renders each message as a dismissible Bulma notification styled by level (debug, info, success, warning, or error). Dismiss buttons use an HTMX inline event to remove the message block from the DOM without a page reload. Views queue only warnings and errors; the other levels are kept for a message someone explicitly asks for.

### `partials/navbar.html`

Renders the main navigation bar with dropdown menus for Alleles, Haplotypes, Diseases, Publications, and Curations (each offering Search and Add links). The right-hand side shows Log In or Log Out and Profile buttons depending on authentication state, plus a link to HLArepo. Includes a small script to enable the responsive burger menu toggle.

### `partials/navbar_link.html`

A micro-partial that renders a single `<a class="navbar-item">` link. It accepts `url` and `text` context variables and applies `has-text-weight-bold` when the link matches the currently active view.

### `partials/public_footer.html`

Renders the HLArepo footer: the shared logos, links to the HLArepo info pages (About, Contact, Citing, Help, Acknowledgements, Collaborators), copyright and funding attribution, a link to the open-source repository, and the current Git SHA. Its text names HLArepo rather than the HCI.

### `partials/public_navbar.html`

Renders the HLArepo navigation bar: a single small, low-emphasis link back to the HCI home page in the upper-right corner. It has no brand link, since the breadcrumb already links to the HLArepo home page, and no burger menu, since there is nothing to collapse.

### `tables.html`

A custom django-tables2 table template that wraps rendered tables in a horizontally scrollable container and replaces the default pagination controls with Bulma-styled previous/next buttons and a numbered page list. It also disables HTMX boosting on table rows to prevent unintended partial-page navigation.
