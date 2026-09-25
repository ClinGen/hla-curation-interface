# Duplicate Pair Validation

## The Problem

A curation links one allele or haplotype to one disease (an "HLA-disease pair").
Nothing stops a curator from creating a second or third curation for a pair that is
already being curated. `CurationCreateForm` in `src/curation/forms.py` is a plain
`ModelForm` with no `clean()` method, `CurationCreate.form_valid` in
`src/curation/views.py` only sets `added_by`, and the `Curation` model has no
uniqueness constraint on `(allele, disease)` or `(haplotype, disease)`. In GitHub #77 a
curator accidentally created a duplicate T1DM / DRB1\*03:01 pair on the test site
because nothing warned them that one already existed.

The requested behavior is:

1. If one curation already exists for the same allele (CAR ID) or haplotype and the
   same disease (Mondo ID), alert the curator. The alert should include the existing
   curation's ID (the `C000123`-style slug) and whether it is a risk or protective
   curation. A second curation is allowed, because the working group allows one pair
   for risk evidence and one for protective evidence.
2. If two curations already exist for the pair, block creation of a third.

Two details of the current code shape the solution:

- **There is no curation-level direction.** "Protective" exists only as
  `Evidence.is_protective`, a per-evidence boolean. A `Curation` has no field that
  says whether it is the risk or the protective curation, so we cannot yet report or
  enforce direction at creation time (a brand-new curation has no evidence at all).
- **Copies share their source's pair.** `curation_copy` (the "copy and recurate"
  workflow from plan 001) creates a new `Curation` with the same allele/haplotype and
  disease and sets `copied_from` to the published source. It calls
  `Curation.objects.create` directly, so it bypasses `CurationCreateForm`. Copies must
  never be blocked, and a copy should not count as a separate pair: it is a new
  version of an existing curation, not a new line of curation.

## The Technical Plan

Validate in `CurationCreateForm.clean()`, because that is the only path for curators to
start a new, independent curation, and it leaves `curation_copy` untouched.

"Existing pairs" means curations with the same disease and the same allele (for allele
curations) or the same haplotype (for haplotype curations). Comparing by foreign key is
equivalent to comparing CAR ID and Mondo ID, because `Allele.car_id`,
`Haplotype.name`, and `Disease.mondo_id` are all unique, and it also works for alleles
whose `car_id` is null. When counting pairs, count only *root* curations
(`copied_from__isnull=True`), so a published curation and its copies count as one
pair.

- Zero existing root curations: create as today.
- One existing root curation: re-render the form with a warning that lists the matching
  curations (slug, status, and a link to each, plus copies of that root) and asks the
  curator to confirm. The form gains an optional `confirm_duplicate` checkbox. It is
  hidden unless there is a match. Submitting again with the box checked creates the
  curation.
- Two or more existing root curations: add a non-field error that lists them and
  refuse to create, whether or not the box is checked.

Showing risk vs. protective in the alert depends on how a curation's direction is
defined (see Open Questions), so that part is a separate, blocked step.

## Alternatives

**Live lookup with HTMX.** When the allele/haplotype and disease selects change, an
HTMX request could fetch and show matching curations before the curator submits. This
is a nicer UX but adds an endpoint, a partial, and JavaScript wiring to the create
page. The confirm-on-submit approach gives the same protection with less code. We can
add the live lookup later on top of the same query helper.

**Database constraint.** A `UniqueConstraint` on `(allele, disease, direction)`
(conditioned on `copied_from IS NULL`) would enforce the rule at the database level.
This only becomes possible if we add a curation-level direction field, and it still
needs the form check to give a friendly message. We can revisit it after the direction
decision.

**Warn after creation.** We could create the curation and show a
`messages.warning`. This is simpler, but the duplicate already exists by the time the
curator sees the warning, which is exactly what #77 wants to avoid.

## Open Questions

1. **How is a curation's direction (risk vs. protective) determined?** Options: (a)
   add a required curation-level field (e.g., `is_protective` or a `direction`
   choice) to `Curation` and `CurationCreateForm`; (b) derive it from included
   evidence's `Evidence.is_protective` (undefined for new or mixed curations). With
   (a), the rule could become "at most one root curation per direction" instead of "at
   most two." This blocks Step 2 only.
2. **Should copies count toward the limit?** This ticket assumes they don't (only
   roots with `copied_from IS NULL` count). If a copy's source is deleted,
   `copied_from` becomes null and the copy becomes a root. That seems acceptable. If
   the user disagrees, only the query in Step 1 changes.
3. **Should the rule apply across curation types?** For example, if an allele-disease
   pair exists, should a haplotype containing that allele trigger a warning? This
   ticket assumes it shouldn't: haplotype pairs are matched only by haplotype.

## Detailed Implementation

### Step 1 — Warn on one match, block on two

#### `src/curation/models.py` — modify

Add a classmethod `Curation.existing_pairs(*, curation_type, allele, haplotype,
disease) -> QuerySet[Curation]`. It returns the root curations
(`copied_from__isnull=True`) with the same disease and the same allele or haplotype
(depending on `curation_type`), ordered by `added_at`. Use `prefetch_related("copies")`
so the template can list each root's copies.

#### `src/curation/forms.py` — modify

Add `confirm_duplicate = forms.BooleanField(required=False, label=...)` to
`CurationCreateForm` and a `clean()` method. After `super().clean()`, if the
allele/haplotype and disease are present, call `Curation.existing_pairs`. Store the
result on `self.existing_pairs` so the template can render it. If there are two or
more, raise a non-field `ValidationError` that names the slugs (e.g., "Two curations
already exist for this pair (C000012, C000034). A third can't be created."). If there
is exactly one and `confirm_duplicate` is false, raise a non-field error asking the
curator to review the existing curation and check the confirmation box.

#### `src/curation/templates/curation/create.html` — modify

Render `form.existing_pairs` (slug linked to `curation-detail`, status, and any
copies) in a Bulma warning box above the submit button. Render the
`confirm_duplicate` checkbox only when exactly one match exists.

#### `src/curation/tests/test_views.py` — modify

Write these tests in `CurationCreateTest` first:

- One existing allele curation: POST without `confirm_duplicate` returns 200, creates
  nothing, and the response contains the existing slug.
- One existing allele curation: POST with `confirm_duplicate=on` creates the curation.
- Two existing allele curations: POST with `confirm_duplicate=on` still creates
  nothing, and the response contains both slugs.
- The same three cases for haplotype curations.
- A published curation plus its copy counts as one pair (a new curation is allowed
  after confirmation).
- A curation for the same allele but a different disease doesn't trigger the warning.

In `CurationCopyTest`, add a test that copying a published curation still succeeds
when two root curations already exist for the pair.

#### `docs/validation.md` — modify

Add the duplicate-pair rule to the Curation high-level summary and to the Curation
"Views"/form details. (While there, note that this doc's `validate_status` entry still
describes the old `DONE` status. The code now checks `READY_FOR_REVIEW`.)

#### `src/curation/README.md` — modify

Update the entries for `forms.py`, `models.py`, `templates/curation/create.html`, and
`tests/test_views.py`.

### Step 2 — Show and enforce direction (blocked on Open Question 1)

If the user picks a curation-level field: add it to `Curation` (with a migration),
`CurationCreateForm.Meta.fields`, `create.html`, the curation detail template, and
`CurationTable` in `src/curation/tables.py`. `curation_copy` must copy the field.
Include the direction in the warning text ("C000012 (risk)"), and change the blocking
rule to "one root curation per direction." Tests: creating a second curation with the
same direction is blocked; the opposite direction is allowed after confirmation;
copies keep the direction. If the user picks derivation from evidence, add a
`Curation.direction` property instead and only display it. Update `docs/validation.md`,
`src/curation/README.md`, and `src/repo/serializers.py` (if the field should be
public).

## Sources

- https://github.com/ClinGen/hla-curation-interface/issues/77
