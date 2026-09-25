# Review Success Messages

## The Problem

The HCI uses Django's messages framework for flash messages, which are rendered by
`src/templates/partials/messages.html` as Bulma message boxes. The box header already
says "Success", "Info", "Warning", or "Error". The messages were written ad hoc, and
their wording is inconsistent. Some say "Added allele." and others say "Disease
added." or "Publication created." Some include the object's ID and most don't. One
says "successfully", which the "Success" header already implies. Some create paths
show no message at all. No test asserts any message text, so the wording can drift
without anything noticing.

The app doesn't use `SuccessMessageMixin` or `success_message` anywhere. Every message
is a direct `messages.<level>()` call. No code calls `messages.debug`, so
`MESSAGE_LEVEL = messages.DEBUG` in `src/config/settings/dev.py` has no effect today.

### Inventory of success and info messages

Each entry lists the file and line, the view, the level, and the text:

- `src/allele/views.py:39`, `AlleleCreate.form_valid`, success: "Added allele."
- `src/haplotype/views.py:46`, `HaplotypeCreate.form_valid`, success: "Added
  haplotype."
- `src/disease/views.py:33`, `DiseaseCreate.form_valid`, success: "Disease added."
- `src/publication/views.py:45`, `PublicationCreate.form_valid` (PubMed branch),
  success: "Publication created."
- `src/publication/views.py:58`, `PublicationCreate.form_valid` (bioRxiv/medRxiv
  branch): no message.
- `src/curation/views.py:60`, `CurationCreate.form_valid`, success: "Curation added."
- `src/curation/views.py:90`, `curation_edit_evidence`, success: "Changes saved
  successfully."
- `src/curation/views.py:102`, `EvidenceCreate.form_valid`: no message.
- `src/curation/views.py:142`, `EvidenceEdit.form_valid`: no message.
- `src/curation/views.py:212`, `curation_publish`, success: "Curation {slug} has been
  published to the repository."
- `src/curation/views.py:237`, `curation_submit`, success: "Curation {slug} has been
  submitted for review."
- `src/curation/views.py:266`, `curation_review` (needs revision), info: "Curation
  {slug} has been sent back for revision."
- `src/curation/views.py:272`, `curation_review` (approved), success: "Curation {slug}
  has been approved."
- `src/curation/views.py:320`, `curation_copy`, success: "Copy created as {slug}."
- `src/auth_/views.py:231`, `phi`, success: "PHI agreement signed."
- `src/auth_/views.py:31`, `login_`, info: "Already logged in."
- `src/auth_/views.py:185`, `:192`, and `:210`, `profile`, `profile_history`, and
  `profile_change`, info: "Not logged in."

For completeness, these are the warning and error messages:

- Warning, external-API failures: `src/allele/views.py:45` ("Oops, something went
  wrong trying to fetch data from the ClinGen Allele Registry. Please try again
  later."), `src/disease/views.py:39` (same, for the Ontology Lookup Service), and
  `src/publication/views.py:63` ("Oops, something went wrong trying to fetch data.
  Please try again later.").
- Error, locking: `src/curation/views.py:82` and `:112` ("This curation is locked and
  cannot be edited."), and `:158` ("This evidence belongs to a locked curation and
  cannot be edited.").
- Error, other: `src/curation/views.py:173` (`EvidenceEdit.form_invalid`, "There was
  an issue with your submission. Please check the form fields."), `:209`
  (`curation_publish`, the raw `ValueError` text from `Curation.transition_to`, e.g.
  "Cannot transition curation from 'INP' to 'PUB'.", which shows internal status
  codes), and `:233` (`curation_submit`, each string from `Curation.can_submit`).

A second problem is ordering. The create views call `messages.success` *before*
`super().form_valid(form)`. That means the message can't include the new object's
slug, which is assigned in `save()`. It also means the message is queued even if the
save then raises.

## The Technical Plan

Adopt a small set of wording rules, apply them to every success and info message, and
add tests that pin the text.

Proposed rules (the user should confirm them, see Open Questions):

1. Success messages use the form "{Entity} {slug} {past-tense verb}.", e.g.
   "Allele A000012 added." Include the human-readable ID whenever an object exists.
2. Use "added" for creation, which matches the UI's "Add Curation" buttons and "Added
   By" labels. Use "saved" for edits, "submitted for review", "approved", "sent back
   for revision", and "published".
3. No "successfully" or "has been". The header already conveys success, and shorter
   is clearer.
4. Sentence case, one sentence, ending with a period.
5. Queue the message only after the save succeeds, so it can include the slug.
6. Every successful create or edit shows a success message, including evidence and
   preprint publications.

Under these rules, "Added allele." becomes "Allele A000012 added." and "Changes saved
successfully." becomes "Evidence for curation C000034 saved." The publish message
becomes "Curation C000034 published to the repository." and "Copy created as C000035."
becomes "Curation C000035 added as a copy of C000034."

## Open Questions

1. **Does the user accept the wording rules and the exact strings above?** Beyond the
   obvious consistency fixes (reordering, adding missing messages, dropping
   "successfully"), the final wording is a product choice. This blocks Step 2.
2. **Should warnings and errors be reviewed in the same pass?** The "Oops" warnings
   and the raw `ValueError` text from `curation_publish` are candidates, but the note
   only mentions success messages. This ticket keeps them out of scope unless the
   user says otherwise. It doesn't block anything.

## Detailed Implementation

### Step 1 — Consistency fixes

#### Create and edit views in five apps — modify

The files are `src/allele/views.py`, `src/haplotype/views.py`, `src/disease/views.py`,
`src/publication/views.py`, and `src/curation/views.py`.

In each `CreateView.form_valid`, call `response = super().form_valid(form)` first,
then queue the message using `self.object.slug`, then return `response`. Add the
missing success messages to the preprint branch of `PublicationCreate.form_valid`,
`EvidenceCreate.form_valid`, and `EvidenceEdit.form_valid` (after the validators pass
and the save succeeds). Drop "successfully" from `curation_edit_evidence`. Keep the
current wording otherwise; Step 2 applies the final strings.

#### Tests — modify

Write tests first in `src/allele/tests.py`, `src/haplotype/tests.py`,
`src/disease/tests.py`, `src/publication/tests/test_views.py`, and
`src/curation/tests/test_views.py`. For each success path, read
`list(get_messages(response.wsgi_request))` (from `django.contrib.messages`) and
assert the level is `SUCCESS` and the text contains the new object's slug. For the
failure paths of the create views, assert that no success message is queued. The
create views that call external APIs already have tests that mock the clients; reuse
those mocks.

#### READMEs — modify

Update the `views.py` and test entries in `src/allele/README.md`,
`src/haplotype/README.md`, `src/disease/README.md`, `src/publication/README.md`, and
`src/curation/README.md` where they describe messages.

### Step 2 — Apply the agreed wording (blocked on Open Question 1)

Change every string in the inventory table to the agreed wording (including the
`auth_` info messages if the user wants them changed). Update the Step 1 tests to
assert the exact strings. If the pattern "{Entity} {slug} {verb}." is adopted, consider
a tiny helper, such as `common.messages.success_for(request, obj, verb)` in a new
`src/common/messages.py` that uses `obj._meta.verbose_name`. Add it only if it removes
real duplication, and document it in `src/common/README.md`.

## Sources

- Notes: "HCI: Review success messages"
