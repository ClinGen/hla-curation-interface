# Validation

This document summarizes all validation applied to each entity in the HCI, including
DB-level constraints, model validators, form validators, and view-level checks.

## High-Level Summary

### Allele

When a curator submits an allele name, the system immediately looks it up in the ClinGen
Allele Registry. If the registry does not recognize the name (or is temporarily
unavailable), the allele is not saved. This ensures that every allele in the HCI is a
real, registry-confirmed entry. The system also prevents two records from sharing the
same name or the same registry ID.

### Haplotype

A haplotype is a combination of alleles, so the system enforces two things when one is
created. First, it automatically arranges the selected alleles into a canonical order
based on their position on chromosome 6, so the same combination always has the same
name regardless of the order the curator picked them in. Second, it rejects the
submission if that exact combination already exists in the system.

### Disease

Disease entries must use the Mondo Disease Ontology. The system checks that a Mondo ID
is provided and that it follows the expected format (it must begin with "MONDO:"). It
then looks the ID up in the EBI Ontology Lookup Service to retrieve the official disease
name and IRI. If the lookup fails, the disease is not saved.

### Publication

Each publication must be one of three types (PubMed article, bioRxiv preprint, or
medRxiv preprint), and the system requires the appropriate identifier for that type: a
PubMed ID for PubMed articles, or a DOI for preprints. Once the identifier is provided,
the system fetches the title, primary author, and publication year from the relevant
external API automatically. If the lookup fails, the publication is not saved. Duplicate
identifiers are also rejected.

### Curation

A curation links one allele or haplotype to one disease. The system makes sure the right
type of genetic entity is provided for the curation type chosen. It also enforces
consistency between a curation's status and its evidence: a curation cannot be marked
"Done" if any of its included evidence records are still "In Progress." When a
classification level is assigned, the system checks that the curation's total score
actually falls within the range permitted for that classification. Once a curation is
published to HLArepo, it becomes read-only and cannot be edited.

### Evidence

Evidence records carry the most validation because they encode the detailed scoring data
from the HLA framework. Key checks include: a preprint publication cannot be marked as
included for scoring; the allele resolution reported in the study cannot be lower than
the resolution of the allele or haplotype being curated; p-values must be entered in a
recognized format and are rejected if they use unsupported comparators; a curator cannot
mark a significant association unless a p-value is present and meets the significance
threshold for the study type (GWAS or non-GWAS); only one effect size statistic (odds
ratio, relative risk, or beta coefficient) may be active at a time; and demographics
must be provided if the typing method is imputation. Evidence belonging to a published
curation is also read-only.

## Nitty-Gritty Details

### Access Control (all entities)

Every create/edit view is protected by `ProtectedViewMixin`
(`src/auth_/permissions.py`). A user must be authenticated and have both
`has_signed_phi_agreement` and `has_curation_permissions` set on their `UserProfile`
(`can_curate == True`). Failing this raises HTTP 403.

### Allele

**DB model** (`src/allele/models.py`):

- `name`: `blank=False`, `unique=True` enforced by Django and the database
- `car_id`: `unique=True` (nullable) enforced at the DB level
- No `clean()` method; no custom model validators

**Form** (`AlleleForm`): standard Django required-field validation on `name`. No
additional form-level `clean`.

**View** (`AlleleCreate.form_valid`): the ClinGen Allele Registry API is called with the
submitted name. If the API returns nothing (unknown allele or network error), the save
is aborted and the user is redirected back with a warning. This is an implicit existence
check. The name must be recognized by the CAR.

### Haplotype

**DB model** (`src/haplotype/models.py`):

- `alleles` M2M: `blank=False` at least one allele required
- `name`: `blank=False`, `unique=True` enforced at DB level
- No `clean()` method; no custom model validators

**Form** (`HaplotypeForm`): exposes `alleles` as a `SelectMultiple`. Standard
required-field validation.

**View** (`HaplotypeCreate.form_valid`): this is where the substantive logic lives:

1. Sorts selected alleles by chromosomal gene order (using the `GENE_LIST` constant) to
   produce a canonical `~`-separated name.
2. Checks for duplicate combinations:
   `Haplotype.objects.filter(name=computed_name).exists()`. If a duplicate exists, adds
   a field error ("A haplotype with these alleles already exists.") and returns
   `form_invalid`.

The computed canonical name is set on the instance. Users never enter the name directly.

### Disease

**DB model** (`src/disease/models.py`): delegates to two model validators in `clean()`.

**Model validators** (`src/disease/validators/models.py`):

- `validate_disease_type_mondo`: If `disease_type == MONDO` and `mondo_id` is empty,
  raises `ValidationError` (required field by type).
- `validate_mondo_id`: If `mondo_id` is present but does not start with `MONDO:`, raises
  `ValidationError` (prefix format check).

**Form** (`DiseaseForm`): exposes only `mondo_id`. Standard required-field validation
from `blank=False`.

**View** (`DiseaseCreate.form_valid`): calls the EBI Ontology Lookup Service. If the API
fails, the save is aborted. The `name` and `iri` fields are populated from the API. They
are never user-entered.

### Publication

**DB model** (`src/publication/models.py`): delegates to three model validators in
`clean()`.

**Model validators** (`src/publication/validators/models.py`):

- `validate_publication_type_pubmed`: type=PubMed requires a non-empty `pubmed_id`.
- `validate_publication_type_biorxiv`: type=bioRxiv requires a non-empty `doi`.
- `validate_publication_type_medrxiv`: type=medRxiv requires a non-empty `doi`.

Each raises a field-specific `ValidationError`. The `pubmed_id` and `doi` fields also
have `unique=True` at the DB level.

**Form** (`PublicationForm`): exposes `publication_type`, `doi`, `pubmed_id`. The
`publication_type` is rendered as radio buttons.

**View** (`PublicationCreate.form_valid`): branches on type to call either the PubMed
E-utilities API or the bioRxiv/medRxiv API. If the API fails, the save is aborted. The
`title`, `author`, and `publication_year` fields are always populated from the external
API, never from user input.

### Curation

**DB model** (`src/curation/models.py`): delegates to three model validators in
`clean()`.

**Model validators** (`src/curation/validators/models/curation.py`):

- `validate_status`: If `status=DONE`, iterates over all evidence and raises
  `ValidationError` if any included evidence (`is_included=True`) still has
  `status=IN_PROGRESS`.
- `validate_curation_type`:
  - If type=ALLELE and `allele` is None, raises an error on the `allele` field.
  - If type=HAPLOTYPE and `haplotype` is None, raises an error on the `haplotype` field.
  - Side effect: clears the unused FK (sets `haplotype=None` for allele curations,
    `allele=None` for haplotype curations).
- `validate_classification`: Checks that the computed score from included evidence falls
  within the allowed range for the chosen classification level. Skipped for new
  (unsaved) records.
  - NO_KNOWN: score must be exactly 0
  - LIMITED: score < 25
  - MODERATE: 25 \<= score \<= 50
  - STRONG / DEFINITIVE: score >= 50

**Views**:

- `CurationEdit.dispatch`: Blocks edits entirely if the curation has been published (has
  a `publication` reverse relation). Redirects with an error message.
- `curation_publish`: Requires `status == DONE` before publishing. Blocks re-publishing
  if already published.

### Evidence

This is the most heavily validated entity, reflecting the complexity of the HLA scoring
framework.

**DB model** (`src/curation/models.py`): delegates to 11 validators in `clean()`.

**Model validators** (`src/curation/validators/models/evidence.py`):

- `validate_publication`: publication FK must not be None.
- `validate_preprint_not_included`: If `is_included=True` and the publication is bioRxiv
  or medRxiv, raises a `ValidationError`. Preprints cannot be counted toward scoring.
- `validate_num_fields`: If `num_fields` is set, it must be >= the minimum resolution
  implied by the allele/haplotype name (colon count + 1). For haplotypes, uses the
  minimum across all constituent alleles.
- `validate_p_value_string`: Parses the free-text p-value field. Accepts exact decimals
  (`0.05`), scientific notation (`5e-8`), and `<` or `<=` prefixed values. Rejects `>`
  and `>=`. Sets `p_value_comparator` and `p_value` (Decimal) on the instance.
- `validate_has_association_and_p_value`: If `has_association=True`, the p-value must be
  present and must fall below the significance threshold. GWAS studies use
  `Intervals.S3A.GWAS_1`; non-GWAS studies use `Intervals.S3A.NON_GWAS_1` (from
  `src/curation/constants/score.py`).
- `validate_effect_size_statistic`: The OR, RR, and beta fields are mutually exclusive.
  Selecting one clears the other two (both the string and Decimal fields).
- `validate_odds_ratio_string`, `validate_relative_risk_string`, `validate_beta_string`,
  `validate_ci_start_string`, `validate_ci_end_string`: Each attempts `Decimal(value)`
  on its string field and raises a `ValidationError` if the string cannot be parsed.

**Form** (`EvidenceEditForm.clean()`):

- If `typing_method == IMPUTATION` and `demographics` is empty, raises a form-level
  `ValidationError`. Demographics are required for imputed typing.

**View** (`EvidenceEdit.form_valid`): runs a second pass of view-layer validators from
`src/curation/validators/views.py` after `form.is_valid()` returns `True`:

- `validate_effect_size_statistic`: same mutual-exclusivity logic, clearing unused
  fields on `form.instance`.
- `validate_has_association_and_p_value`: calls the shared
  `has_association_and_p_value_err_msg` function and adds errors to the form object
  rather than raising `ValidationError`.
- `validate_odds_ratio`, `validate_relative_risk`, `validate_beta`, `validate_ci_start`,
  `validate_ci_end`: each calls `maybe_to_decimal()` and sets the parsed Decimal onto
  `form.instance`.

If any form errors exist after this second pass, returns `form_invalid`. The view-layer
validators exist because `form_valid` runs after model `clean()`. This second pass is
needed to set the Decimal fields and re-check the has-association constraint using the
freshly parsed p-value.

`EvidenceEdit.dispatch` also blocks all edits if the parent curation has been published.
