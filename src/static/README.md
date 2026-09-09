# `static`

This directory contains all static assets served by the Django application, organized under `hci/`. It includes third-party CSS frameworks and icon libraries, custom application styles, font files, images (logos, favicons, and icons), and JavaScript libraries. A web app manifest is also included here to support progressive web app metadata.

### `hci/css/bootstrap-icons.css`

The Bootstrap Icons icon font stylesheet. It defines CSS classes and `@font-face` rules that map icon names to glyphs in the accompanying WOFF/WOFF2 font files.

### `hci/css/bulma.css`

The full Bulma CSS framework stylesheet. It provides a modern, flexbox-based layout system and component styles used throughout the application.

### `hci/css/choices.css.map`

The source map for the Choices.js CSS bundle. It maps the minified styles back to their original source locations to aid in browser-based debugging.

### `hci/css/choices.min.css`

The minified Choices.js stylesheet. It provides the styles for the Choices.js custom select/multi-select widget used in the application's forms.

### `hci/css/custom.css`

Application-specific CSS overrides and utility classes. It defines styles for entity-type logo sizing, footer logo containers, and a horizontal scroll container.

### `hci/css/fonts/bootstrap-icons.woff`

The Bootstrap Icons icon font in WOFF format. It is referenced by `bootstrap-icons.css` and served as a fallback for browsers that do not support WOFF2.

### `hci/css/fonts/bootstrap-icons.woff2`

The Bootstrap Icons icon font in WOFF2 format. It is the preferred, more compressed version referenced by `bootstrap-icons.css`.

### `hci/img/android-chrome-192x192.png`

A 192×192 pixel PNG version of the application icon. It is used by Android Chrome when a user adds the site to their home screen, as declared in `site.webmanifest`.

### `hci/img/android-chrome-512x512.png`

A 512×512 pixel PNG version of the application icon. It is used by Android Chrome for higher-resolution home screen and splash screen contexts, as declared in `site.webmanifest`.

### `hci/img/apple-touch-icon.png`

The application icon in the format expected by Apple devices. It is displayed when a user adds the site to their iOS home screen.

### `hci/img/biorxiv-logo.png`

The logo for bioRxiv, a preprint server for biology. It is displayed in the interface when linking to or citing bioRxiv preprints as evidence sources.

### `hci/img/car-logo.png`

The logo for the Classification, Assertion, and Reporting (CAR) system or a related entity. It is used in the interface to identify that data source or partner organization.

### `hci/img/clingen-logo-with-text.svg`

The ClinGen logo including its text wordmark, in SVG format. It is used in the application header or footer to identify the ClinGen organization.

### `hci/img/favicon-16x16.png`

A 16×16 pixel PNG favicon. It is displayed in browser tabs and bookmarks at small sizes.

### `hci/img/favicon-32x32.png`

A 32×32 pixel PNG favicon. It is displayed in browser tabs and bookmarks at standard sizes, and on higher-DPI displays.

### `hci/img/favicon.ico`

The application favicon in ICO format. It provides broad browser compatibility as the default fallback icon for browser tabs and bookmarks.

### `hci/img/hci-logo-circle.png`

The HLA Curation Interface logo in a circular crop. It is used in contexts that require a square or circular icon, such as the web app manifest icons.

### `hci/img/hci-logo.png`

The primary HLA Curation Interface logo. It is used in the application header and other branding contexts.

### `hci/img/medrxiv-logo.png`

The logo for medRxiv, a preprint server for health sciences. It is displayed in the interface when linking to or citing medRxiv preprints as evidence sources.

### `hci/img/mondo-logo.png`

The logo for the Mondo Disease Ontology. It is displayed in the interface when referencing disease classifications sourced from the Mondo ontology.

### `hci/img/pubmed-logo.svg`

The PubMed logo in SVG format. It is displayed in the interface when linking to or citing PubMed literature as evidence sources.

### `hci/img/stanford-medicine-logo.png`

The Stanford Medicine logo. It is displayed in the application footer or about page to acknowledge institutional affiliation.

### `hci/img/under-construction.gif`

An animated "under construction" GIF. It is used as a placeholder on pages or features that are not yet complete.

### `hci/js/callback.js`

A bundled JavaScript file for handling the Clerk authentication OAuth callback flow. It contains the React and Clerk SDK code required to complete sign-in after redirecting back from an external identity provider.

### `hci/js/choices.js`

The full, unminified source of the Choices.js library (v11.2.3). It provides a customizable, accessible replacement for native `<select>` elements, used in the application's forms.

### `hci/js/choices.min.js`

The minified production build of the Choices.js library. It is the version loaded in production to reduce page load time.

### `hci/js/htmx.js`

The htmx library (v2.0.10). It enables HTML-first, AJAX-driven interactivity by allowing Django template elements to issue HTTP requests and swap content without a full page reload.

### `hci/js/sign-in.js`

A bundled JavaScript file for rendering the Clerk sign-in component. It contains the React and Clerk SDK code needed to mount the embedded sign-in UI on the application's login page.

### `hci/site.webmanifest`

The web app manifest for the HLA Curation Interface. It declares the application name, short name, theme colors, display mode, and icon paths so that browsers can treat the site as an installable progressive web app.
