# Contract (Smoke) Tests for the Allele and Disease Clients

## The Problem

The HCI calls three external APIs, each through a `clients.py` module:

- `src/publication/clients.py`: NCBI PubMed E-utilities (plus bioRxiv/medRxiv).
  `fetch_pubmed_data`, `get_pubmed_title`, `get_pubmed_author`, `get_pubmed_year`,
  `fetch_rxiv_data`, `get_rxiv_*`. **Has live tests** in
  `src/publication/tests/test_clients.py`.
- `src/allele/clients.py`: ClinGen Allele Registry (CAR). `fetch_allele_data`,
  `get_car_id`. **No live tests.**
- `src/disease/clients.py`: EBI Ontology Lookup Service (OLS), Mondo ontology.
  `fetch_disease_data`, `get_name`, `get_iri`. **No live tests.**

`haplotype` has no `clients.py` and makes no external calls. Clerk
(`src/auth_/views.py`) is a vendor SDK that needs real credentials, not a `clients.py`
module, so it is out of scope.

The publication tests are what the note calls "smoke tests". The code calls them
contract tests. Each class is decorated with `@unittest.skipIf(SKIP_CONTRACT_TESTS,
SKIP_REASON)`, where `SKIP_CONTRACT_TESTS = os.getenv("RUN_CONTRACT_TESTS") != "1"`, so
they are skipped in normal runs. CI sets `RUN_CONTRACT_TESTS: 0` in
`.github/workflows/ci.yml`. Nothing in the pytest config (`pyproject.toml`) marks them.
The skip is done only by the environment variable.

The allele and disease views are only tested with `fetch_*` mocked
(`src/allele/tests.py` and `src/disease/tests.py`). If CAR or OLS changes its URL or
response shape (as happened with the CAR URL, commit `5008130`), the test suite stays
green while adding an allele or disease breaks in production. So the client modules that
still need contract tests are **`src/allele/clients.py`** and
**`src/disease/clients.py`**.

## The Technical Plan

Copy the publication pattern. Move the skip constants into `src/common/tests.py` so all
three apps share one definition. Convert `allele` and `disease` from a single `tests.py`
to a `tests/` package, as `publication` and `curation` already use, and add
`tests/test_clients.py` to each. Each test calls the live API with known-good inputs and
checks the parsed values. Add a `just` recipe that runs only the contract tests.

Known-good values, checked against the live APIs on 2026-09-25:

- CAR: `fetch_allele_data("B*57:01:01")` returns a list whose first item has `"id":
  "XAHLA718811387"`. The CAR rejects names with the `HLA-` prefix
  (`"HLA-B*57:01:01"` returns HTTP 400), so the test should also assert that
  `fetch_allele_data("HLA-B*57:01:01")` returns `None`.
- OLS: `fetch_disease_data("MONDO:0005147")` returns a term with `label` "type 1
  diabetes mellitus" and `iri` `http://purl.obolibrary.org/obo/MONDO_0005147`.

## Alternatives

**Add `test_clients.py` next to the existing `tests.py`.** `python_files` in
`pyproject.toml` includes `test_*.py`, so `src/allele/test_clients.py` would be
collected without moving anything. This is less churn, but it would leave three
different test layouts in the project.

## Detailed Implementation

### Step 1 — Share the skip constants

#### `src/common/tests.py` — modify

Add `SKIP_CONTRACT_TESTS` and `SKIP_REASON`, moved from
`src/publication/tests/test_clients.py`.

#### `src/publication/tests/test_clients.py` — modify

Import `SKIP_CONTRACT_TESTS` and `SKIP_REASON` from `common.tests` instead of defining
them.

#### `justfile` — modify

Add a `test-contract` recipe in the `test` group:
`RUN_CONTRACT_TESTS=1 uv run pytest -k Contract`.

#### `src/common/README.md`, `README.md` or `docs/how-to.md` — modify

Document the shared constants and the new recipe.

### Step 2 — CAR contract tests

#### `src/allele/tests.py` → `src/allele/tests/test_views.py` — move

Use `git mv`, and add an empty `src/allele/tests/__init__.py`.

#### `src/allele/tests/test_clients.py` — create

Add `CarContractTest(unittest.TestCase)` decorated with `skipIf(SKIP_CONTRACT_TESTS,
SKIP_REASON)`. It should include `test_fetch_allele_data_returns_list`,
`test_get_car_id_extracts_id` (for `B*57:01:01`, expect `XAHLA718811387`), and
`test_fetch_allele_data_rejects_hla_prefix`. Use a `CAR_TEST_CASES` list and `subTest`,
as the publication tests do.

#### `src/allele/README.md` — modify

Replace the `tests.py` entry with `tests/__init__.py`, `tests/test_views.py`, and
`tests/test_clients.py` entries.

### Step 3 — OLS contract tests

#### `src/disease/tests.py` → `src/disease/tests/test_views.py` — move

Use `git mv`, and add an empty `src/disease/tests/__init__.py`.

#### `src/disease/tests/test_clients.py` — create

Add `OlsContractTest` with `test_fetch_disease_data_returns_dict`,
`test_get_name_extracts_label`, and `test_get_iri_extracts_iri` for `MONDO:0005147`.
Also add `test_fetch_disease_data_returns_none_for_unknown_id`: OLS returns HTTP 404 for
`MONDO:9999999` (checked 2026-09-25), so `fetch_disease_data` returns `None`.

#### `src/disease/README.md` — modify

Make the same README changes as for `allele`.

Verify with `RUN_CONTRACT_TESTS=1 just test-contract` locally. `just ci` must still
pass, with the new tests skipped.

## Sources

- Notes: "HCI: Write smoke tests for client modules. I think we have smoke tests for the
  `publication` app. Need similar tests for the other client modules. Make a list of
  client modules that need smoke tests."
