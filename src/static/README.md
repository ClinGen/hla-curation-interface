# `static`

This directory contains the static assets served by Django for the HLA
Curation Interface (HCI): vendored CSS and JavaScript libraries, project
imagery (logos, favicons, third-party source logos), web fonts, and the
PWA web app manifest. All assets live under a single `hci/` namespace
subdirectory so that Django's `collectstatic` produces predictable,
collision-free URLs (e.g. `/static/hci/img/hci-logo.png`).

### `hci/css/bootstrap-icons.css`

Vendored Bootstrap Icons stylesheet. Defines the `bi-*` icon font
classes used throughout the templates and references the WOFF/WOFF2
files in `hci/css/fonts/`.

### `hci/css/bulma.css`

Vendored Bulma CSS framework. Provides the base styling, layout, and
component classes (containers, columns, buttons, forms, tables, etc.)
used by the HCI templates.

### `hci/css/choices.css.map`

Source map for `choices.min.css`. Lets browser dev tools map the
minified rules back to the original Choices.js stylesheet.

### `hci/css/choices.min.css`

Minified stylesheet for the Choices.js library. Styles the enhanced
`<select>` widgets used on curation, allele, haplotype, disease, and
publication forms.

### `hci/css/custom.css`

Project-specific CSS overrides on top of Bulma. Defines
`.entity-type-logo` (sizing for inline source logos like Mondo,
PubMed), `.footer-logo-container` (padding for the footer logos), and
`.scroll-container` (horizontally scrollable wrapper used for wide
tables).

### `hci/css/fonts/bootstrap-icons.woff`

WOFF font file for Bootstrap Icons. Referenced by
`bootstrap-icons.css` as a fallback for browsers that do not support
WOFF2.

### `hci/css/fonts/bootstrap-icons.woff2`

WOFF2 font file for Bootstrap Icons. The primary, compressed font file
referenced by `bootstrap-icons.css`.

### `hci/img/android-chrome-192x192.png`

192x192 PNG home-screen icon for Android Chrome, referenced from
`site.webmanifest`.

### `hci/img/android-chrome-512x512.png`

512x512 PNG home-screen icon for Android Chrome, referenced from
`site.webmanifest`.

### `hci/img/apple-touch-icon.png`

PNG touch icon used by iOS Safari when the site is added to the home
screen.

### `hci/img/biorxiv-logo.png`

Logo for bioRxiv, displayed alongside publication entries whose source
is bioRxiv.

### `hci/img/car-logo.png`

Logo for the ClinGen Allele Registry (CAR), displayed alongside allele
entries that link out to CAR.

### `hci/img/clingen-logo-with-text.svg`

ClinGen wordmark logo (SVG), shown in the site footer.

### `hci/img/favicon-16x16.png`

16x16 PNG favicon used by browsers that prefer a PNG favicon at this
size.

### `hci/img/favicon-32x32.png`

32x32 PNG favicon used by browsers that prefer a PNG favicon at this
size.

### `hci/img/favicon.ico`

Multi-resolution ICO favicon used by browsers (and Windows shortcuts)
that request `/favicon.ico`.

### `hci/img/hci-logo-circle.png`

Circular variant of the HCI logo, used in contexts that require a
round avatar-style mark.

### `hci/img/hci-logo.png`

Primary HCI logo, displayed in the site header.

### `hci/img/medrxiv-logo.png`

Logo for medRxiv, displayed alongside publication entries whose source
is medRxiv.

### `hci/img/mondo-logo.png`

Logo for the Mondo Disease Ontology, displayed alongside disease
entries that link out to Mondo.

### `hci/img/pubmed-logo.svg`

Logo for PubMed (SVG), displayed alongside publication entries whose
source is PubMed.

### `hci/img/stanford-medicine-logo.png`

Stanford Medicine logo, shown in the site footer alongside the ClinGen
logo to acknowledge institutional affiliation.

### `hci/img/under-construction.gif`

Animated GIF placeholder shown on pages or sections that are not yet
implemented.

### `hci/js/choices.js`

Unminified source of the Choices.js library, kept alongside the
minified build for debugging.

### `hci/js/choices.min.js`

Minified build of Choices.js. Powers the enhanced searchable select
widgets used on the various curation forms.

### `hci/js/htmx.js`

Vendored htmx library. Provides the `hx-*` attributes used by the
templates to perform partial-page updates (e.g. autocomplete and
search-as-you-type) without a full page reload.

### `hci/site.webmanifest`

PWA web app manifest. Declares the application name (`HLA Curation
Interface`), short name (`HCI`), the Android home-screen icons,
theme/background colors, and `standalone` display mode.
