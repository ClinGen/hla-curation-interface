# Remove Preprint Publications from Add Publication

## The Problem

The Add Publication page (`publication/create.html`) asks the curator to choose a
publication type ("PubMed Article", "bioRxiv Paper", or "medRxiv Paper") before entering
an identifier. Preprints are never used for assertions: evidence from a preprint can't
be included in a curation (`validate_preprint_not_included` in
`src/curation/validators/models/evidence.py`). At the 07/24 HLA meeting, the group
decided to remove the bioRxiv and medRxiv choices. With only PubMed left, the Type radio
group is pointless and should go too. The PubMed ID help text should also warn curators
not to enter preprints that happen to be indexed in PubMed. This is flagged as a
priority because Katrin wants to record a walkthrough without the preprint options on
screen.

The goal is a form with a single PubMed ID input whose help text reads: "The PubMed ID
for the publication, e.g., 11910336. Do not use PubMed IDs of preprint articles, only
enter PubMed IDs of peer-reviewed publications."

## The Technical Plan

This is a form-and-view change, not a schema change. `Publication.publication_type`
stays on the model, with its `PUB`/`BIO`/`MED` choices and its default of `PUB`, so
existing preprint rows stay valid and `validate_preprint_not_included` keeps protecting
curations that already reference them. `PublicationForm` drops `publication_type` and
`doi` and exposes only a required `pubmed_id`. The DOI input was already hidden by
JavaScript whenever "PubMed Article" was selected, so PubMed publications never had a
DOI entered through the UI anyway. The new sentence is added through the form's
`help_texts`, so no migration is needed. `PublicationCreate.form_valid` keeps only the
PubMed branch. The rxiv warning partial and the show/hide JavaScript are deleted.

Once nothing in the UI can create a preprint, the bioRxiv/medRxiv client functions are
dead code. The plan is to delete them and their contract tests in a separate cleanup
step (see Open Question 1). We keep `PublicationTypes`, the model validators, and the
evidence-level preprint validator because existing data still depends on them.

## Alternatives

**Change the model's `help_text` instead of the form's.** This would also update the
admin, but Django records `help_text` in migrations, so it would need a migration that
does nothing to the database. The sentence is guidance for data entry, so it belongs on
the form.

**Drop `publication_type` from the model.** This needs a data migration and a decision
about what to do with existing preprint rows, and it would break the evidence validator.
It doesn't make sense until Open Question 2 is answered.

## Open Questions

1. Should the bioRxiv/medRxiv client code (`fetch_rxiv_data`, `get_rxiv_title`,
   `get_rxiv_author`, `get_rxiv_year`, `BIORXIV_URL`, `MEDRXIV_URL`) and its contract
   tests be deleted, or kept in case preprints come back? Recommendation: delete them,
   since git history keeps them. This blocks Step 3. **Answer (2026-09-25): Delete
   them.** Preprints aren't expected to come back.
2. What should happen to preprint publications that already exist in production? The
   local dev database (`src/hci.db`) has 400 `BIO` and 400 `MED` rows, but those look
   like seed data. Production counts are unknown. Options: (a) keep them as legacy rows
   (the default in this ticket), (b) also hide them from the Add Evidence publication
   dropdown (`EvidenceCreateForm`), or (c) delete them. This blocks Step 4, which only
   happens if the answer is (b). **Answer (2026-09-25): (c) Delete them.** The user
   expects none in the test or production database. Step 4 is skipped in favor of
   Step 5.

## Detailed Implementation

### Step 1 — Tests first

#### `src/publication/tests/test_views.py` — modify

In `PublicationCreateTest.expected_text`, remove "Publication Type", "bioRxiv Paper",
"medRxiv Paper", "PubMed Article", and "DOI". Add the new sentence "Do not use PubMed
IDs of preprint articles, only enter PubMed IDs of peer-reviewed publications." Add a
test that the rendered page contains no `name="publication_type"` or `name="doi"`
inputs. Delete `test_creates_biorxiv_publication_with_valid_form_data` and
`test_creates_medrxiv_publication_with_valid_form_data`. Change
`test_creates_pubmed_publication_with_valid_form_data` to post only
`{"pubmed_id": "123"}` and still assert `publication_type == "PUB"`. Change
`test_does_not_create_publication_with_invalid_form_data` to post `{"pubmed_id": ""}`.
Add a test that posting `{"publication_type": "BIO", "doi": "10.1101/123"}` does not
create a publication and that `fetch_pubmed_data` is not called.

### Step 2 — PubMed-only form and view

#### `src/publication/forms.py` — modify

Set `fields = ["pubmed_id"]`, remove the `RadioSelect` widget, and add
`help_texts = {"pubmed_id": "The PubMed ID for the publication, e.g., 11910336. Do not
use PubMed IDs of preprint articles, only enter PubMed IDs of peer-reviewed
publications."}`. Override `__init__` to set `self.fields["pubmed_id"].required = True`.
The model field is `blank=True` because preprints have no PubMed ID.

#### `src/publication/views.py` — modify

In `PublicationCreate.form_valid`, set `form.instance.publication_type =
PublicationTypes.PUBMED` explicitly and remove the bioRxiv/medRxiv `elif` branch and the
`fetch_rxiv_data`/`get_rxiv_*` imports.

#### `src/publication/templates/publication/create.html` — modify

Remove the `publication_type` radio include, the `doi-div` block, and the whole
`<script>` block. Keep only the `pubmed_id` text input (with `show_help=True`) and the
submit button.

#### `src/publication/templates/publication/partials/rxiv_warning.html` — delete

This partial is only used by `create.html`.

#### `src/publication/README.md` — modify

Update the entries for `forms.py`, `templates/publication/create.html`,
`tests/test_views.py`, and `views.py`, and remove the `partials/rxiv_warning.html`
entry. Update the overview to say new publications are PubMed-only and that preprint
rows are legacy data.

#### `docs/validation.md`, `docs/design.md`, `src/README.md` — modify

Update the publication sections to say that curators can only add PubMed articles, and
that `BIO`/`MED` types remain only for legacy records.

### Step 3 — Remove preprint client code (blocked by Open Question 1)

#### `src/publication/clients.py` — modify

Delete `BIORXIV_URL`, `MEDRXIV_URL`, `fetch_rxiv_data`, `get_rxiv_title`,
`get_rxiv_author`, and `get_rxiv_year`, plus the `PublicationTypes` import if nothing
else uses it.

#### `src/publication/tests/test_clients.py` — modify

Delete `BIORXIV_TEST_CASES`, `MEDRXIV_TEST_CASES`, `BioRxivContractTest`, and
`MedRxivContractTest`, and update the module docstring.

#### `src/publication/README.md`, `src/static/README.md` — modify

Update the `clients.py` and `tests/test_clients.py` entries. `hci/img/biorxiv-logo.png`
and `hci/img/medrxiv-logo.png` aren't referenced by any template, so delete them and
their `src/static/README.md` entries in the same commit.

### Step 4 — Hide preprints from Add Evidence (only if the answer to OQ 2 is (b))

#### `src/curation/forms.py` — modify

In `EvidenceCreateForm.__init__`, limit `self.fields["publication"].queryset` to
`Publication.objects.filter(publication_type=PublicationTypes.PUBMED)`. First, write a
test in `src/curation/tests/test_views.py` that the Add Evidence page does not list the
`BIO`/`MED` fixture publications (pk 2 and 3 in `test_publications.json`). Update
`src/curation/README.md`.

Fixtures: `src/publication/fixtures/test_publications.json` keeps its `BIO`/`MED` rows
because `src/curation/tests/test_models.py`
(`test_cannot_include_biorxiv_publication` and related tests) uses them to exercise the
legacy-preprint validator.

### Step 5 — Delete preprint publications (the answer to OQ 2)

#### `src/publication/migrations/0004_delete_preprint_publications.py` — create

A `RunPython` data migration that deletes `Publication` rows whose type is `BIO` or
`MED`. `Evidence.publication` uses `on_delete=CASCADE`, so deleting a cited preprint
would silently delete its evidence. Instead, the migration raises a `RuntimeError`
listing the cited preprints' slugs, which rolls the migration back. The reverse is a
no-op. The migration depends on the latest curation migration so that `Evidence` is in
the migration state. Historical publication records are kept.

#### `src/publication/tests/test_migrations.py` — create

Test that the migration function deletes the `BIO`/`MED` fixture rows and keeps the
`PUB` row, and that it raises and deletes nothing when evidence cites a preprint.

The model's `BIO`/`MED` choices, their validators, and `validate_preprint_not_included`
stay for now, so the fixtures and curation tests are unchanged.

### Step 6 — Remove `publication_type`, `doi`, and the preprint validators

After Step 5, the user decided (2026-09-25) to remove the preprint leftovers too. No
evidence cites a preprint on the test or production site.

#### `src/publication/migrations/0005_remove_publication_type_and_doi.py` — create

Removes `publication_type` and `doi` from `Publication` and `HistoricalPublication` and
makes `pubmed_id` non-null and required. Before altering `pubmed_id`, a `RunPython`
step deletes historical records with no PubMed ID (the history of the preprints
deleted in Step 5), since they would block the `NOT NULL` change.

#### Code — modify or delete

Delete `src/publication/constants/` (`PublicationTypes`, `PUBLICATION_TYPE_CHOICES`),
`src/publication/validators/` (the per-type validators), and curation's
`validate_preprint_not_included`. Remove `doi` from the admin, the list table, the list
search fields, the detail template, and the repo serializer's evidence publication.
`PublicationForm` no longer needs to override `required`. The fixture keeps only the
`PUB` row, and the preprint tests in `src/curation/tests/test_models.py` are deleted.

#### Tests

`src/publication/tests/test_migrations.py` now runs 0004 against the migration state
before it, since the current model has no `publication_type`. New
`src/publication/tests/test_models.py` checks that `pubmed_id` is required.

## Sources

- https://github.com/ClinGen/hla-curation-interface/issues/86
