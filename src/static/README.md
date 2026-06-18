# `static`

This directory contains all static assets served by the application, organized under
`hci/`. It includes vendored third-party CSS and JavaScript libraries, project-specific
custom styles, web fonts, and image assets such as logos, favicons, and PWA icons.

### `hci/css/bootstrap-icons.css`

Vendored Bootstrap Icons stylesheet that maps icon class names to the corresponding web
font glyphs used throughout the UI.

### `hci/css/bulma.css`

Vendored Bulma CSS framework stylesheet that provides the utility classes, layout
system, and component styles used as the primary UI framework.

### `hci/css/choices.css.map`

Source map for the Choices.js CSS, used by browser developer tools to map minified
styles back to their original source locations.

### `hci/css/choices.min.css`

Vendored minified stylesheet for the Choices.js library, which styles the enhanced
select-box components used in forms.

### `hci/css/custom.css`

Project-specific stylesheet that defines custom rules for entity-type logo image sizing,
footer logo container spacing, and a horizontal-scroll container class used for wide
tables.

### `hci/css/dataTables.dataTables.min.css`

Vendored minified stylesheet for the DataTables jQuery plugin, which styles the sortable
and searchable data tables used on list pages.

### `hci/css/fonts/bootstrap-icons.woff`

Bootstrap Icons web font in WOFF format, referenced by `bootstrap-icons.css` for broader
browser compatibility.

### `hci/css/fonts/bootstrap-icons.woff2`

Bootstrap Icons web font in WOFF2 format, referenced by `bootstrap-icons.css` as the
preferred modern font format.

### `hci/img/android-chrome-192x192.png`

192x192 px PNG version of the HCI logo, used as the Android Chrome home-screen icon and
referenced in `site.webmanifest`.

### `hci/img/android-chrome-512x512.png`

512x512 px PNG version of the HCI logo, used as the high-resolution Android Chrome
home-screen icon and referenced in `site.webmanifest`.

### `hci/img/apple-touch-icon.png`

PNG icon used when a user adds the site to the home screen on an Apple iOS device.

### `hci/img/biorxiv-logo.png`

Logo image for bioRxiv, used to identify bioRxiv preprint publications in the UI.

### `hci/img/car-logo.png`

Logo for the ClinGen Allele Registry (CAR), used to link out to or identify CAR allele
identifiers in the UI.

### `hci/img/clingen-logo-with-text.svg`

SVG logo for the Clinical Genome Resource (ClinGen), including the organization's name
text; displayed in the site footer.

### `hci/img/favicon-16x16.png`

16x16 px PNG favicon for the site, linked in the base template for standard browser tab
display.

### `hci/img/favicon-32x32.png`

32x32 px PNG favicon for the site, linked in the base template for higher-resolution
browser tab display.

### `hci/img/favicon.ico`

ICO-format favicon for the site, provided for legacy browser compatibility.

### `hci/img/hci-logo-circle.png`

Circular variant of the HLA Curation Interface logo, used where a round icon format is
needed.

### `hci/img/hci-logo.png`

Standard rectangular version of the HLA Curation Interface logo.

### `hci/img/medrxiv-logo.png`

Logo image for medRxiv, used to identify medRxiv preprint publications in the UI.

### `hci/img/mondo-logo.png`

Logo for the Mondo Disease Ontology, used to identify or link to Mondo disease terms in
the UI.

### `hci/img/pubmed-logo.svg`

SVG logo for PubMed, used to identify or link to PubMed publication records in the UI.

### `hci/img/stanford-medicine-logo.png`

Stanford Medicine logo image, displayed in the site footer as an institutional
affiliation.

### `hci/img/under-construction.gif`

Animated "under construction" GIF used to indicate pages or features that are not yet
complete.

### `hci/js/choices.js`

Vendored unminified source of the Choices.js library, which enhances native `<select>`
elements with search and custom styling.

### `hci/js/choices.min.js`

Vendored minified production build of Choices.js, loaded by the base template for
enhanced select inputs.

### `hci/js/dataTables.bulma.min.js`

Vendored minified DataTables integration plugin that applies Bulma CSS classes to
DataTables-generated markup.

### `hci/js/dataTables.min.js`

Vendored minified DataTables jQuery plugin used to add sorting, searching, and
pagination to HTML tables on list pages.

### `hci/js/htmx.js`

Vendored HTMX library that enables AJAX-driven partial page updates via HTML attributes,
used throughout the application to avoid full page reloads.

### `hci/js/jquery.min.js`

Vendored minified jQuery library, required as a dependency by DataTables.

### `hci/site.webmanifest`

Web app manifest file that defines the application's name ("HLA Curation Interface"),
short name ("HCI"), home-screen icons, theme color, and standalone display mode for PWA
installation support.
