# Max-Length Constants

## The Problem

Every `max_length` in the project is a bare number literal in a `models.py` file, and
some of them have explanatory comments (e.g., `max_length=28,  # A CAR allele ID is of
the form XAHLA718827727. 14 characters.`). The same values repeat across apps. For
example, `max_length=7` for the `C000123`-style `slug` appears on six models, and
`max_length=3` for choice codes appears on ten fields. Nothing ties a choice field's
`max_length` to the length of its choice codes. The goal is to give each length a
name in the app's constants module, so the numbers are documented once and reused.

No `max_length` appears in any `forms.py` or template. The model forms inherit their
lengths from the models, so this ticket only changes models and constants.

### Inventory

Slugs (`max_length=7`, format `X` plus six digits, set in each model's `save()`):
`Allele.slug` (`src/allele/models.py`), `Haplotype.slug`
(`src/haplotype/models.py`), `Disease.slug` (`src/disease/models.py`),
`Publication.slug` (`src/publication/models.py`), and `Curation.slug` and
`Evidence.slug` (`src/curation/models.py`).

Choice-code fields (`max_length=3`): `Curation.status`, `Curation.curation_type`,
`Curation.ep_classification`, `Evidence.status`, `Evidence.typing_method`,
`Evidence.multiple_testing_correction`, `Evidence.effect_size_statistic`,
`Evidence.additional_phenotypes`, `Disease.disease_type`, and
`Publication.publication_type`. Two-character choice codes (`max_length=2`):
`Evidence.zygosity` and `Evidence.p_value_comparator`.

Other fields:

- `src/allele/models.py`: `Allele.name` 60, and `Allele.car_id` 28.
- `src/haplotype/models.py`: `Haplotype.name` 240.
- `src/disease/models.py`: `Disease.mondo_id` 26, `Disease.iri` 88, and
  `Disease.name` 256.
- `src/publication/models.py`: `Publication.pubmed_id` 16, `Publication.doi` 128,
  `Publication.title` 256, and `Publication.author` 16.
- `src/curation/models.py`: `Curation.ep` 5 (five-digit EP ID), `Demographic.group`
  20, `Evidence.p_value_string` 40, and `Evidence.odds_ratio_string`,
  `relative_risk_string`, `beta_string`, `ci_start_string`, and `ci_end_string` 10
  each.
- `src/auth_/models.py`: `UserProfile.clerk_user_id` 255.

### Existing constants modules

`src/curation/constants/models/` (`common.py`, `curation.py`, `evidence.py`),
`src/disease/constants/models.py`, `src/haplotype/constants/models.py`, and
`src/publication/constants/models.py` already hold each app's model constants.
`src/allele` and `src/auth_` have no constants package, and `src/common` has no
constants module.

## The Technical Plan

Put each constant next to the other constants for the same model, and put the one
truly shared value in `common`:

- Create `src/common/constants.py` with `SLUG_MAX_LENGTH = 7` (documenting the
  prefix-plus-six-digits format) and `CHOICE_CODE_MAX_LENGTH = 3` (for three-letter
  choice codes).
- Add app-specific constants to the existing modules, and move each explanatory
  comment from the model to the constant: `src/disease/constants/models.py`
  (`MONDO_ID_MAX_LENGTH`, `IRI_MAX_LENGTH`, `DISEASE_NAME_MAX_LENGTH`),
  `src/haplotype/constants/models.py` (`HAPLOTYPE_NAME_MAX_LENGTH`),
  `src/publication/constants/models.py` (`PUBMED_ID_MAX_LENGTH`, `DOI_MAX_LENGTH`,
  `TITLE_MAX_LENGTH`, `AUTHOR_MAX_LENGTH`), `src/curation/constants/models/curation.py`
  (`EP_ID_MAX_LENGTH`), and `src/curation/constants/models/evidence.py`
  (`DEMOGRAPHIC_GROUP_MAX_LENGTH`, `P_VALUE_STRING_MAX_LENGTH`,
  `DECIMAL_STRING_MAX_LENGTH`, `ZYGOSITY_MAX_LENGTH`,
  `P_VALUE_COMPARATOR_MAX_LENGTH`).
- Create `src/allele/constants/__init__.py` and `src/allele/constants/models.py`
  (`ALLELE_NAME_MAX_LENGTH`, `CAR_ID_MAX_LENGTH`), following the other apps.
- For `UserProfile.clerk_user_id`, either create `src/auth_/constants.py`
  (`CLERK_USER_ID_MAX_LENGTH = 255`) or leave it (see Open Questions).

**Migrations.** Keep every value the same, and no migration will be generated.
Django's autodetector compares the deconstructed field arguments, and a constant with
the same value deconstructs identically. This also holds for the
`django-simple-history` historical models. Verify this with
`uv run python src/manage.py makemigrations --check --dry-run`, which must report "No
changes detected" once the existing drift described in Step 1 is fixed. Changing any
value *would* need an `AlterField` migration for the model and for its historical
model.

## Open Questions

1. **Should any values change while we're here?** Two look small:
   `Publication.author` (16) can't hold longer surnames, and `Publication.title` (256)
   can't hold some long titles. Both are filled from PubMed or bioRxiv data in
   `PublicationCreate.form_valid`, not typed by the user. SQLite doesn't enforce
   `max_length`, and the form excludes these fields from validation, so today nothing
   fails. They would fail on PostgreSQL. This ticket keeps every value unchanged (no
   migrations). Changing values would be a separate follow-up. This doesn't block the
   refactor.
2. **Does the one `auth_` field warrant a constants module?** Doesn't block. The
   default is to create `src/auth_/constants.py` for consistency.

## Detailed Implementation

### Step 1 — Introduce the constants and use them

#### `src/common/tests.py` — modify

Write a test first: `call_command("makemigrations", "--check", "--dry-run")` raises no
`SystemExit`. (`makemigrations --check` exits nonzero when there are changes.) This
permanently guards against accidental schema drift and proves that this refactor
changed nothing.

**Existing drift.** As of this writing, `makemigrations --check --dry-run` already
reports changes: `AlterField` on `Evidence.num_fields` and
`HistoricalEvidence.num_fields`. The choice labels changed in commit f85bc1d ("Fix
allele res labels", #74), and no migration was generated. So the guard test fails
at first. Land the guard test together with that migration as a separate first
commit, before the constants refactor. The migration changes only choice labels, so
it doesn't alter the database.

The follow-up in `docs/plans/001-ep-review.md` also plans a `0021` migration
(`0021_rename_status_codes`) that would pick up this drift, and its Open Question 1
asks whether that name must be kept because an earlier version was applied somewhere.
Wait for that decision. If the name must be kept, fold the drift fix and guard test
into that migration's bead instead. Otherwise, generate
`curation/migrations/0021_alter_evidence_num_fields_and_more.py` here, and the status
rename becomes `0022`.

#### `src/common/constants.py` — create

Add a module docstring, `SLUG_MAX_LENGTH`, and `CHOICE_CODE_MAX_LENGTH`.

#### Constants modules — create or modify

Create `src/allele/constants/__init__.py`, `src/allele/constants/models.py`, and
possibly `src/auth_/constants.py`. Modify `src/disease/constants/models.py`,
`src/haplotype/constants/models.py`, `src/publication/constants/models.py`,
`src/curation/constants/models/curation.py`, and
`src/curation/constants/models/evidence.py` as described in the plan. Give each
constant a short comment that explains the value (these replace the inline comments
in the models).

#### `models.py` in each of the six apps — modify

Replace each literal with the constant and remove the moved comment. The apps are
`allele`, `haplotype`, `disease`, `publication`, `curation`, and `auth_`.

#### READMEs — modify

Add `constants.py` to `src/common/README.md` and `constants/` to
`src/allele/README.md` (and `src/auth_/README.md` if created). Update the constants
entries in `src/disease/README.md`, `src/haplotype/README.md`,
`src/publication/README.md`, and `src/curation/README.md`.

Verification: `makemigrations --check --dry-run` reports no changes, and `just ci`
passes.

## Sources

- Notes: "HCI: Add max lengths to constants module"
