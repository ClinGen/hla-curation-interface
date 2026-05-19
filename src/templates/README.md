# `templates`

This directory contains the project-level Django templates for the HLA
Curation Interface (HCI). It holds the shared base layout that every
page extends, the small partials that the layout pulls in (navbar,
footer, flash messages, account-activation banner), and the generic
HTTP error pages (400, 403, 404, 500). App-specific templates live
under each Django app's own `templates/` subdirectory; only the
cross-cutting, site-wide templates live here.

### `400.html`

Template rendered for HTTP 400 (Bad Request) responses. Extends
`layouts/base.html`, sets the title and description blocks for the
error, and shows a Bulma warning message with a link back to the home
page.

### `403.html`

Template rendered for HTTP 403 (Forbidden) responses. Branches on the
current user's state to show a tailored message: prompting anonymous
visitors to log in or sign up, telling inactive users to email
`hci@clinicalgenome.org` for activation, telling users without
curation permissions to request them and sign the PHI agreement, and
otherwise showing a generic "no permission" message.

### `404.html`

Template rendered for HTTP 404 (Not Found) responses. Extends
`layouts/base.html` and shows a Bulma warning message indicating that
the page does not exist, with a link back to the home page.

### `500.html`

Template rendered for HTTP 500 (Internal Server Error) responses.
Extends `layouts/base.html` and shows a Bulma danger message asking
the user to try again later and to email `hci@clinicalgenome.org`
with details if the problem persists.

### `layouts/base.html`

The site-wide base layout that every page extends. Declares the HTML
shell, sets the `HCI | …` title pattern, wires up the CSRF token for
htmx requests, loads the vendored CSS (Bulma, custom, Bootstrap
Icons, Choices.js) and JS (htmx, Choices.js, jQuery, DataTables),
links the favicons, Apple touch icon, and PWA `site.webmanifest`, and
defines the page structure: header (with `partials/navbar.html`),
main (with the account-activation banner, flash messages, and a
`main` block for child templates), and footer (with
`partials/footer.html`).

### `partials/account_activation.html`

Banner shown to authenticated users whose account is not fully
activated. Included near the top of `<main>` in
`layouts/base.html`. Lists the outstanding activation steps: signing
the PHI agreement (linking to the `phi` page) and/or requesting
curation permissions (via email to `hci@clinicalgenome.org`), and
links to the HLA curation standard operating procedure.

### `partials/footer.html`

Site footer included by `layouts/base.html`. Shows the ClinGen and
Stanford Medicine logos, navigation columns for the About, Contact,
Citing, Help, Acknowledgements, and Collaborators pages, the
copyright line, funding/management acknowledgement
(NIH/NHGRI, U24HG009649), a link to the GitHub source and the MIT
license, and the current `GIT_SHA` build identifier.

### `partials/messages.html`

Renders Django's `messages` framework as dismissible Bulma message
cards. Branches on the message tag (`debug`, `info`, `success`,
`warning`, `error`) to pick the appropriate Bulma color modifier and
Bootstrap Icon, and uses htmx `hx-on-click` to let the user dismiss
each message by removing its enclosing block.

### `partials/navbar.html`

Primary site navigation included by `layouts/base.html`. Provides the
mobile burger toggle, a `Home` link, dropdowns with `Search` and
`Add` items for Alleles, Haplotypes, Diseases, Publications, and
Curations, and a right-aligned button group with `Log In` / `Log Out`
+ `Profile` (depending on auth state) and an `HLArepo` shortcut.
Inlines the small JavaScript snippet from the Bulma docs that wires
up the burger toggle, rebound to the `htmx:load` event so it keeps
working across htmx-driven page swaps.

### `partials/navbar_link.html`

Tiny reusable partial for an individual navbar entry. Takes a `url`
name and `text` via `{% with %}`, resolves the URL with `{% url %}`,
and adds `has-text-weight-bold` to the link when the current view
matches so the active page is visually highlighted.
