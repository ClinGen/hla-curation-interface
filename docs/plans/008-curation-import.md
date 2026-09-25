# Curation Import

## The Problem

Every curation in the HCI today is entered by hand, one form at a time: a curator adds
the allele (or haplotype), the disease, and each publication, then creates a curation,
adds evidence items, and fills in the evidence edit form field by field. There is no
way to bring in curations that already exist elsewhere. The main source of such
curations is the set of concordance spreadsheets that curators filled out before the
HCI existed. Re-keying them by hand is slow and error prone.

The spreadsheets are also dirty. The same concept is written differently from one
spreadsheet to the next: one spreadsheet has "4" in the resolution column, another has
"4-field"; allele names may or may not carry the `HLA-` prefix and may contain stray
spaces (e.g., `DRB1 *03:01`); yes/no columns use "Y", "yes", "TRUE", or "x"; typing
methods are written as free text rather than the HCI's three-letter codes. None of
these values can be written straight into the database.

The repo has no management commands today (there is no `management/` directory in any
app), and the only bulk-loading mechanism is Django fixtures loaded by the
`django-loaddata-test` and `django-loaddata-prod` recipes in the `justfile`. Those
fixtures are hand-written JSON with hard-coded primary keys and slugs, which works for
test data and the fixed list of demographics, but not for real curations.

There is also an ownership question. Every model has an `added_by` foreign key to
`User`, which the views set to `request.user`. An import has no request, so we must
decide which user the imported records belong to.

The goal is a simple, repeatable, internal-only way to import curations and their
evidence from a normalized file, with a cleaning layer that absorbs the spreadsheet
mess, a dry run that reports problems before anything is written, and enough
bookkeeping that running the same import twice does not create duplicates.

## The Technical Plan

The import is a Django management command, `import_curations`, in the `curation` app.
It is internal only: a developer runs it on the server (or locally against a copy of
the database) with `uv run manage.py import_curations path/to/file`. There is no web UI.

The command works in three stages.

**Read.** A reader turns the input file into a list of plain Python row objects. Each
row describes one evidence item plus the curation it belongs to: the allele name or
haplotype name, the Mondo ID, the PubMed ID (or DOI for a preprint), and the evidence
fields (resolution, zygosity, typing method, p-value, effect size, cohort size, and so
on), along with an import key that identifies the curation in the source. The exact
input format is still an open question (see below), so the reader is isolated behind a
single function and the rest of the pipeline only sees row objects.

**Normalize.** A normalization module maps each dirty cell to the value the HCI stores.
It is a set of small, pure functions, one per concept: `normalize_num_fields` turns
"4", "4-field", "4 Field", and "four" into the integer `4`; `normalize_allele_name`
strips the `HLA-` prefix and whitespace; `normalize_bool` handles the yes/no variants;
`normalize_typing_method` maps free-text labels to `TypingMethod` codes using the
labels in `TYPING_METHOD_CHOICES` plus a small table of known synonyms; and so on.
Anything a function can't map is reported as an error on that row rather than guessed.
Because these are pure functions, they are easy to test exhaustively, and new synonyms
found in future spreadsheets are a one-line change.

**Validate and write.** For each curation group, the importer finds or creates the
supporting records, then creates the curation and its evidence. Alleles, diseases, and
publications are looked up by their natural keys (allele `name`, `mondo_id`,
`pubmed_id` or `doi`). If one doesn't exist, the importer creates it the same way the
create views do, by calling the existing clients (`allele.clients.fetch_allele_data`,
`disease.clients.fetch_disease_data`, `publication.clients.fetch_pubmed_data` and
`fetch_rxiv_data`) to fill in the CAR ID, disease name, and publication metadata.
Haplotypes are found or created from their constituent alleles, using the same gene
ordering as `HaplotypeCreate.form_valid`. Evidence fields are validated through the
same code paths the edit view uses: the importer builds an `EvidenceEditForm` from the
normalized data, calls `is_valid()`, then runs the view-level helpers in
`curation.validators.views` (`validate_effect_size_statistic`, `validate_odds_ratio`,
and so on). That way an imported evidence item passes exactly the same checks as one
typed in by a curator, and when we add new validation, the importer gets it for free.

Everything runs inside one database transaction. With `--dry-run`, the command does all
of the work, including validation, then rolls the transaction back and prints the
report. Without it, the command commits only if every row is valid. Partial imports are
not allowed, so the database is never left half-imported. External lookups can't be
rolled back, but they are read-only, so that is fine.

The report lists, for every row, whether it would create or reuse each supporting
record, whether it would create a curation or skip it as already imported, and any
normalization or validation errors, with the source row number. It ends with totals.

**Idempotency.** Each imported curation records where it came from, so a second run of
the same file skips curations that were already imported instead of duplicating them.
We add a nullable, unique `import_key` field to `Curation` (e.g.,
`concordance-a:17`), set only by the importer. On a re-run, rows whose curation
`import_key` already exists are reported as "already imported" and skipped. Evidence
items don't need their own key because they are always created together with their
curation.

**Attribution.** The command takes a required `--user` option (a username or email of
an existing Django user). Every created record's `added_by` is set to that user, and
the simple-history records are attributed to the same user with a change reason of
"Imported from `<file name>`" (simple-history reads `_history_user` and
`_change_reason` off the instance before saving). Which user that should be is an open
question below.

**Status.** Imported curations are created as `IN_PROGRESS`, and imported evidence
keeps the model's default `needs_review=True`, so a curator must look over every
imported item before the curation can be submitted for expert panel review via the
normal workflow (`Curation.can_submit`). Whether imports should ever be able to create
already-reviewed or published curations is an open question.

## Alternatives

**Django fixtures.** The issue asks whether this could just be fixtures. Fixtures are
the right tool for fixed reference data like `curation/fixtures/demographics.json`, but
they are a poor fit here. A fixture must already contain the stored codes (`"MO"`,
`"HRT"`, `4`), primary keys, foreign-key primary keys, and slugs, so all of the cleaning
work would have to happen in some other script that writes the fixture, and that
script is most of this plan anyway. `loaddata` also saves objects in raw mode, which
skips our `save()` overrides (so slugs like `C000123` are never generated) and skips
`clean()` and form validation entirely. It has no dry run and no way to look up an
existing allele by name. Fixtures would work for moving data from one HCI database to
another, but that is the backup and restore plan's job, not this one.

**A web upload page.** A page where a curator uploads a spreadsheet would remove the
need for server access, but it adds a file upload surface, a long-running request
(each new allele, disease, and publication calls an external API), and UI for the
report. The spreadsheets are a one-time (or rare) migration, so a command is enough. If
imports become routine, the importer's core function can later be called from a view.

**Reading the raw spreadsheets directly.** We could point the command at the original
`.xlsx` files and put per-spreadsheet column mappings in code. That couples the HCI to
spreadsheets that aren't in the repo and whose layouts we don't control. It is simpler
to agree on one normalized format and convert each spreadsheet to it once (by hand or
with a throwaway script), letting the normalization layer handle cell-level mess.

## Open Questions

1. **Input format.** CSV (one row per evidence item, with curation columns repeated) or
   nested JSON (one object per curation containing a list of evidence)? CSV is what the
   spreadsheets export to and what curators can edit; JSON represents the
   curation-to-evidence nesting and multi-valued fields such as demographics without
   delimiter conventions. The recommendation is CSV as the only supported format, with
   demographics as a semicolon-separated list, but this needs the user's input. This
   blocks Step 2 and everything after it. The exact column list also depends on what
   the concordance spreadsheets actually contain, which we can't see because they are
   not in the repo.
2. **Owning user.** Should imported records belong to (a) a dedicated service user such
   as `hci-import` that is never used to log in, (b) the curator who filled out the
   spreadsheet, passed per run with `--user`, or (c) a per-row `curator` column matched
   to existing users by email? The plan assumes a single `--user` per run, which
   supports (a) and (b). This blocks Step 4.
3. **Status of imported curations.** Should imports always create `IN_PROGRESS`
   curations with `needs_review=True` evidence (the plan's assumption), or should some
   concordance curations come in already reviewed, with an EP classification or even
   published? Importing as published would bypass the EP review workflow in
   `docs/plans/001-ep-review.md` and would need `PublishedCuration` records. This
   blocks Step 4.
4. **Idempotency key.** Is a per-curation `import_key` field acceptable, and what
   should its values be (source file name plus row or group number, or an ID column
   the spreadsheets already have)? The alternative is to match on allele or haplotype
   plus disease, but the HCI allows more than one curation for the same pair (see
   GitHub #77), so that match is ambiguous. This blocks Step 1.
5. **Missing external data.** If the ClinGen Allele Registry, OLS, or PubMed can't be
   reached, or returns nothing for a value, should the row fail (the plan's
   assumption), or should the record be created without the fetched data? This affects
   Step 3.

## Detailed Implementation

### Step 1 — Add `import_key` to `Curation`

#### `src/curation/tests/test_models.py` — modify

Add tests first: `import_key` defaults to `None`; two curations can both have
`None`; two curations with the same non-null `import_key` raise `IntegrityError`.

#### `src/curation/models.py` — modify

Add `import_key = models.CharField(max_length=128, null=True, blank=True, unique=True,
verbose_name="Import Key", help_text=...)` to `Curation`. It is `null=True` so that
the many curations created by hand don't collide on an empty string (add the same
`# ruff: ignore[django-nullable-model-string-field]` comment the EP fields use, with a
short explanation). It is not added to any form, so curators never see or edit it.
Run `just django-makemigrations` to generate the migration, which also updates the
historical model.

#### `src/curation/admin.py` — modify

Show `import_key` as a read-only field in the `Curation` admin so a developer can see
where a curation came from.

#### `src/curation/README.md` — modify

Mention the new field in the `models.py` description.

### Step 2 — Normalization functions

#### `src/curation/imports/__init__.py` — create

Empty package marker.

#### `src/curation/imports/normalize.py` — create

Pure functions, each taking a raw string and returning the stored value or raising a
`NormalizationError` (defined in this module) with a message naming the bad value:

- `normalize_allele_name(raw)` — strip whitespace, drop a leading `HLA-`, remove
  spaces around `*`, reject anything without a `*`.
- `normalize_haplotype_name(raw)` — split on `~`, normalize each part.
- `normalize_mondo_id(raw)` — accept `MONDO:0005052`, `MONDO_0005052`, and
  `0005052`; return `MONDO:0005052`, which passes `validate_mondo_id` in
  `disease/validators/models.py`.
- `normalize_pubmed_id(raw)` — strip a `PMID:` prefix and whitespace; digits only.
- `normalize_num_fields(raw)` — accept `1`-`4`, `N-field`, `N field`, `N-Field`,
  spelled-out numbers; return an int in `NumFields`.
- `normalize_bool(raw)` — "y", "yes", "true", "1", "x" are `True`; "n", "no",
  "false", "0", and empty are `False`; anything else is an error.
- `normalize_zygosity(raw)`, `normalize_typing_method(raw)`,
  `normalize_multiple_testing_correction(raw)`,
  `normalize_effect_size_statistic(raw)`, `normalize_additional_phenotypes(raw)` —
  case-insensitive match against the codes and labels in
  `curation/constants/models/evidence.py`, plus a module-level synonyms dict for each
  (e.g., `"hi-res"` to `TypingMethod.HIGH_RES_TYPING`).
- `normalize_demographics(raw)` — split the list and match each entry to a
  `Demographic.group` case-insensitively.

Numeric strings (p-value, odds ratio, CI bounds) are passed through with whitespace
trimmed; the existing validators parse them.

#### `src/curation/tests/test_imports.py` — create

Write these tests first. Table-driven tests for every function, covering each known
variant (including the "4" versus "4-field" case from the issue and `DRB1 *03:01`) and
at least one rejected value per function.

#### `src/curation/README.md` — modify

Describe the `imports/` package and `normalize.py`.

### Step 3 — Reader and row model

#### `src/curation/imports/rows.py` — create

A `ImportRow` dataclass holding the normalized values for one evidence item plus its
curation fields (`import_key`, `curation_type`, `allele_name` or `haplotype_name`,
`mondo_id`, `pubmed_id` or `doi`, and the evidence fields), and the source row number.
A `read_rows(path) -> tuple[list[ImportRow], list[RowError]]` function that opens the
file in the agreed format (Open Question 1), maps columns to fields, runs the
normalizers, and collects `RowError(row_number, column, message)` objects instead of
stopping at the first error. Unknown or missing required columns are reported as a
file-level error. `group_rows(rows)` groups rows by `import_key` and checks that every
row in a group agrees on the curation-level columns.

#### `src/curation/tests/test_imports.py` — modify

Tests using small files written to a temporary directory: a valid file produces the
expected rows; a missing column is reported; a bad cell is reported with its row number
and column; rows in one group that disagree on the disease are reported.

#### `src/curation/README.md` — modify

Describe `rows.py`.

### Step 4 — Importer and management command

#### `src/curation/imports/importer.py` — create

`import_rows(groups, user, source_name, dry_run) -> ImportReport`. Inside
`transaction.atomic()`:

- For each group, skip it (and record "already imported") if a `Curation` with that
  `import_key` exists.
- Find or create the allele, haplotype, disease, and publications. Creation mirrors the
  create views: `fetch_allele_data` plus `get_car_id`, `fetch_disease_data` plus
  `get_name` and `get_iri`, `fetch_pubmed_data` or `fetch_rxiv_data` plus the title,
  author, and year helpers. Extract the haplotype-naming logic in
  `HaplotypeCreate.form_valid` into a function in `haplotype/models.py` (for example,
  `Haplotype.name_from_alleles(alleles)`) so the view and the importer share it; update
  the view to call it.
- Create the `Curation` with `status=Status.IN_PROGRESS`, `added_by=user`, and the
  `import_key`, and call `full_clean()` before saving.
- For each row, create the `Evidence` with `curation` and `publication`, then build an
  `EvidenceEditForm(data=..., instance=evidence)`, call `is_valid()`, run the helpers
  from `curation.validators.views` in the same order as `EvidenceEdit.form_valid`, and
  save. Form errors become report errors with the source row number.
- Set `_history_user = user` and `_change_reason = f"Imported from {source_name}"` on
  each instance before saving so the audit log shows who imported it.
- At the end, if there are any errors or `dry_run` is set, call
  `transaction.set_rollback(True)`.

`ImportReport` is a dataclass with per-row outcomes, errors, and totals, and a
`render()` method that returns plain text for the command to print.

#### `src/curation/management/__init__.py` — create

Empty package marker.

#### `src/curation/management/commands/__init__.py` — create

Empty package marker.

#### `src/curation/management/commands/import_curations.py` — create

`Command(BaseCommand)` with a positional `path` argument, a required `--user` (username
or email; error if no such user), and `--dry-run`. It calls `read_rows`, stops with the
error list if the file is malformed, calls `group_rows` and `import_rows`, prints the
report, and exits non-zero if there were any errors.

#### `src/curation/tests/test_imports.py` — modify

Tests first, with the external clients patched (`unittest.mock.patch` on the functions
as imported in `importer.py`), following the style of the existing view tests:

- A valid file creates the expected curations, evidence, and supporting records, with
  `added_by` and history user set to the given user.
- Existing alleles, diseases, and publications are reused, not duplicated.
- A second run of the same file creates nothing and reports every curation as already
  imported.
- `--dry-run` writes nothing but reports the same outcomes.
- One invalid row (e.g., imputation without demographics, or `has_association` with a
  non-significant p-value) causes nothing to be written.
- A failed external lookup is reported as an error on that row.
- Imported curations are `IN_PROGRESS` and imported evidence has `needs_review=True`.
- An unknown `--user` exits with an error. Use `django.core.management.call_command`.

#### `src/haplotype/tests.py` — modify

Test the extracted naming function, and keep the existing `HaplotypeCreate` tests
passing.

#### `src/curation/README.md`, `src/haplotype/README.md` — modify

Describe `importer.py`, the `management/` directory and the command, and the new
haplotype naming function.

### Step 5 — Document the import format and add a recipe

#### `src/curation/README.md` — modify

Add a short "Importing curations" section: the columns, which are required, the
accepted variants for each normalized column, how `import_key` works, and an example
invocation with `--dry-run`. Keep it within the 88-character text width.

#### `justfile` — modify

Add a `django-import-curations path user` recipe in the `django` group that runs
`cd src && uv run manage.py import_curations {{path}} --user {{user}} --dry-run`, and a
second recipe (or a flag argument) for the real run, so the dry run is the default.

## Sources

- https://github.com/ClinGen/hla-curation-interface/issues/63
- https://github.com/ClinGen/hla-curation-interface/issues/77 (why allele or
  haplotype plus disease isn't a unique key)
