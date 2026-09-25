# Fix Copy-Paste Mistakes in the Client Modules

## The Problem

`get_car_id` in `src/allele/clients.py` extracts the ClinGen Allele Registry (CAR) ID
from a CAR response. When the ID is missing, it logs:

```python
logger.warning("Unable to get name from OLS data; returning None")
```

This text was copied from `src/disease/clients.py`, which does talk to OLS. It names the
wrong service ("OLS" instead of "CAR") and the wrong field ("name" instead of "CAR ID").
That's misleading when someone is reading logs to debug a failed allele creation. The
mistake is still present at `src/allele/clients.py:53`.

A related copy-paste mistake goes the other way. The module docstring of
`src/disease/clients.py` says "Houses code that interacts with third-party services for
the allele app." It should say "disease app". `haplotype` has no `clients.py`, and
`src/publication/clients.py` has no such mistakes.

## The Technical Plan

Correct both strings, and add a unit test that pins the log message so the mistake
can't come back.

## Detailed Implementation

### Step 1 — Test first

#### `src/allele/tests.py` — modify

(If ticket 005 has already moved this file, use `src/allele/tests/test_clients.py`
instead, in a class that is not skipped by `SKIP_CONTRACT_TESTS`.) Add a
`GetCarIdTest(unittest.TestCase)` with these tests:

- `get_car_id([{"id": "XAHLA123"}])` returns `"XAHLA123"` and logs nothing;
- for `None`, `[]`, and `[{}]`, it returns `None`, and
  `self.assertLogs("allele.clients", level="WARNING")` captures
  "Unable to get CAR ID from CAR data; returning None";
- the captured message does not contain "OLS".

### Step 2 — Fix the strings

#### `src/allele/clients.py` — modify

Change the warning in `get_car_id` to
`"Unable to get CAR ID from CAR data; returning None"`.

#### `src/disease/clients.py` — modify

Change the module docstring to "Houses code that interacts with third-party services
for the disease app."

#### `src/allele/README.md` — modify

Update the `tests.py` entry to mention the `get_car_id` unit tests. The `clients.py`
entry doesn't need to change.

## Sources

- Notes: "HCI: Fix log message. In allele/clients.py:53: logger.warning("Unable to get
  name from OLS data; returning None"). This is in a CAR function, not an OLS function.
  It should say "CAR data" not "OLS data"."
