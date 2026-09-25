# Improve Demographics

## The Problem

The note says only "Improve demographics," so the intent must be confirmed before any
code changes. This ticket records the current state, the pain points that are visible
in the code, and candidate improvements for the user to choose from.

### Current state

- **Model.** `Demographic` in `src/curation/models.py` has one field, `group`
  (`max_length=20`, unique). Its docstring says it holds "the biogeographic groups in
  Huddart et al. 2019." The groups come from `src/curation/fixtures/demographics.json`,
  which has seven groups: American, East Asian, European, Central/South Asian, Near
  Eastern, Oceanian, and Sub-Saharan African. The fixture must be loaded by hand
  (`docs/how-to.md` says "Make sure the demographics fixtures are loaded").
- **Evidence fields.** `Evidence` has `demographics` (a many-to-many to `Demographic`
  through the `evidence_demographic_map` table), `demographics_text_quotes` (a
  `TextField` added in commit 9c2ae76 for GitHub #78), and `demographics_notes`.
- **Form.** `EvidenceEditForm` in `src/curation/forms.py` renders `demographics` as a
  searchable `SelectMultiple`. `EvidenceEditForm.clean()` requires demographics when
  `typing_method` is imputation, and requires text quotes whenever demographics are
  selected.
- **Templates.** `src/curation/templates/evidence/edit.html` shows the group select,
  then text quotes, then notes. `src/curation/templates/evidence/partials/data.html`
  shows the three values on the evidence detail page.
- **Publishing.** `serialize_evidence` in `src/repo/serializers.py` publishes the
  group names only. Text quotes were deliberately removed from the public output in
  commit 88ce6df, at the request of the #78 reporter, "until we have a more structured
  way to capture the data."
- **Scoring.** Demographics don't feed into any scoring step in `src/curation/score.py`.

### Pain points visible in the code

1. **Structure is coarse.** A curator can say *which* groups a study included, but
   not how many participants (or cases and controls) came from each group. The #78
   thread explicitly calls the text-quotes field a stopgap until the data is captured
   in a more structured way.
2. **The group list may be incomplete.** Huddart et al. 2019 (the PharmGKB
   biogeographic groups) also defines admixed groups, such as African
   American/Afro-Caribbean and Latino, that aren't in the fixture. Verify this against
   the paper. "African American/Afro-Caribbean" wouldn't fit in `max_length=20`.
3. **Field order doesn't match the request in #78.** The issue asked for the quotes
   field to be "the first field right under the header," but `edit.html` renders it
   after the group select.
4. **The rules aren't visible up front.** The two rules in
   `EvidenceEditForm.clean()` chain together: a curator who picks imputation must
   select groups, and a curator who selects groups must add quotes. They learn this one
   error at a time, because neither `help_text` (`Evidence.demographics`,
   `Evidence.demographics_text_quotes`) mentions the requirement.
5. **Groups can't be added without a migration or admin.** New groups require
   editing the fixture and re-running `loaddata`, or using the Django admin.

### Candidate improvements

- **A. Quick wins:** move the text-quotes field above the group select; state the
  requirements in the help text ("Required if groups are selected," "Required if the
  typing method is imputation"); and name and link the source of the groups (Huddart
  et al. 2019).
- **B. Complete the group list:** add the missing Huddart groups to the fixture (and a
  data migration so existing deployments get them), and raise `Demographic.group`'s
  `max_length` (this needs a schema migration).
- **C. Structured demographics:** replace the plain many-to-many with a through model,
  such as `EvidenceDemographic(evidence, demographic, sample_size, case_count,
  control_count)`, edited through an inline formset on the evidence edit page. Update
  `Evidence.copy_to` and the serializer to match. This is the largest option and
  probably what the "more structured way" in #78 refers to.
- **D. Publish more:** after C, decide whether the structured data (and possibly the
  quotes) should be public in `src/repo/serializers.py` and the repo templates.

## The Technical Plan

Get a decision first (see Open Questions). Then implement the chosen options as
separate beads. Option A is independent and small. B and C both change the schema and
should each be one reviewable change with migrations. D depends on C.

## Open Questions

1. **What does "improve demographics" mean?** Which of options A through D (or
   something else) does the user want, and what structured fields does the working
   group need per group (sample size, cases and controls, country, self-reported vs.
   genetic ancestry)? This blocks all implementation.
2. **Is Huddart et al. 2019 still the grouping the working group wants?** #78 says
   "we have not decided on specific groupings." This blocks option B.

## Detailed Implementation

This section is provisional until Open Question 1 is answered. It describes options A
and C, the two most likely choices.

### Step 1 — Quick wins (option A)

#### `src/curation/templates/evidence/edit.html` — modify

Render `form.demographics_text_quotes` first in the Demographics box, then the group
select, then notes. (`common/form/select/search.html` always renders `help_text`, so
the new help text below appears without template changes.)

#### `src/curation/models.py` — modify

Update `help_text` on `Evidence.demographics` and `Evidence.demographics_text_quotes`
to state when each is required and where the groups come from. Changing `help_text`
generates a migration (Django tracks it), so run `makemigrations`.

#### `src/curation/tests/test_views.py` — modify

Write tests first in `EvidenceEditTest`: the quotes field is rendered before the
demographics select (compare the indexes of their `name=` attributes in the GET
response), and the response contains the new help text. Also add the missing
test for the imputation rule (imputation with no groups is rejected with "Demographics
must be provided if typing method is imputation."). The existing
`test_requires_text_quotes_when_demographics_provided` must still pass.

#### `src/curation/README.md` — modify

Update the `models.py` and `templates/evidence/edit.html` entries. (Migrations are
ignored by the READMEs.)

### Step 2 — Structured demographics (option C, only if chosen)

#### `src/curation/models.py` — modify

Add an `EvidenceDemographic` through model with history, and point
`Evidence.demographics` at it. Write a migration that moves existing
`evidence_demographic_map` rows into the new table with null counts. Update
`Evidence.copy_to` to copy the through rows.

#### `src/curation/forms.py`, `views.py`, and `templates/evidence/edit.html` — modify

Add an inline formset for `EvidenceDemographic` to `EvidenceEdit`, and keep the
imputation rule (at least one row is required).

#### `src/repo/serializers.py` — modify

Serialize the structured rows if the user wants them public (option D).

#### Tests and READMEs

Add model tests in `src/curation/tests/test_models.py` (through-model creation and
`copy_to` copying rows), view tests for the formset, and serializer tests in
`src/repo/tests.py`. Update `src/curation/README.md` and `src/repo/README.md`.

## Sources

- Notes: "HCI: Improve demographics"
- https://github.com/ClinGen/hla-curation-interface/issues/78 (closed; context for the
  text-quotes field)
