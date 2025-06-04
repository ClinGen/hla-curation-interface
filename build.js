/**
 * Builds our JavaScript dependencies and puts them into the static directory where
 * Django expects them to be. This script assumes you're in the root directory of
 * the repository.
 */

import { copyFile } from "node:fs/promises";

const CSS_STATIC_DIR = "./src/static/hci/css";
const JS_STATIC_DIR = "./src/static/hci/js";
const JS_SRC_DIR = "./src/js";

// Build JavaScript dependencies.
await Bun.build({
  entrypoints: [`${JS_SRC_DIR}/firebase.js`],
  outdir: JS_STATIC_DIR,
});

// Copy HTMX into our Django static directory.
const htmxPath = "./node_modules/htmx.org/dist/htmx.min.js";
await copyFile(htmxPath, `${JS_STATIC_DIR}/htmx.js`);

// Copy Bulma into our Django static directory.
const bulmaPath = "./node_modules/bulma/css/bulma.min.css";
await copyFile(bulmaPath, `${CSS_STATIC_DIR}/bulma.css`);
