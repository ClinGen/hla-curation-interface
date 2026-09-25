# Stable IDs Instead of HCI IDs

## The Problem

Every major model in the HCI has an "HCI ID": a `slug` field (verbose name
"Human-Readable ID") that `save()` fills in from the primary key the first time the
object is saved. The prefix says what kind of object it is:

| Model         | Prefix | Example   | External stable ID                          |
| ------------- | ------ | --------- | ------------------------------------------- |
| `Allele`      | `A`    | `A000001` | `car_id` (CAR ID), nullable; also `name`    |
| `Haplotype`   | `H`    | `H000001` | none (`name` is derived from its alleles)   |
| `Disease`     | `D`    | `D000001` | `mondo_id`, required and unique             |
| `Publication` | `P`    | `P000001` | `pubmed_id` or `doi`, each nullable, unique |
| `Curation`    | `C`    | `C000001` | none                                        |
| `Evidence`    | `E`    | `E000001` | none                                        |

HCI IDs are used everywhere: every detail, history, and change URL (e.g.,
`/disease/<slug>/detail`, `/curation/<curation_slug>/evidence/<evidence_slug>/detail`,
`/repo/<curation_slug>/detail`); the "ID" link column in every `tables.py`; the
`search_fields` of every `SearchListView`; page titles and breadcrumbs in every
detail, history, and change template; `HistoryTable` change links in
`common/tables.py`; and the public repo JSON built by
`repo/serializers.py::serialize_published_curation`, which exposes `slug` for the
allele, haplotype, haplotype alleles, disease, and publication, plus `curation_id`,
`evidence_id`, and `copied_from` as HCI IDs. Curators also refer to curations by their
"C number" in conversation and in GitHub issues (see #77).

For entities that already have an identifier everyone in the field uses, the HCI ID is
a second name for the same thing. A curator looking at a disease wants `MONDO:0005052`,
not `D000017`, and a publication is known by its PMID. Showing both is noise, and the
HCI ID is the one nobody outside the HCI recognizes. The idea, from the user's notes,
is to get rid of HCI IDs for entities that have stable IDs.

There are also a couple of weaknesses in the HCI IDs themselves: `slug` is not
`unique=True` in any model, so nothing in the database prevents a duplicate; and
`max_length=7` means the format breaks after 999,999 objects of a type (not a practical
concern, but it shows the IDs were not designed as permanent public identifiers).

This is a speculative idea. The goal of this plan is to record which entities could
drop HCI IDs, what that would cost, and a low-risk path if the user decides to do it.

## The Technical Plan

The HCI ID does two jobs today: it is the key in URLs, and it is the label shown to
curators. (The database key is the integer `pk`, which HCI IDs are derived from.) The
recommended approach keeps the integer primary keys and the `slug` columns in the
database, and switches the URL key and the displayed label to the external ID wherever
one exists and is reliable.

**Which entities qualify.**

- **Disease** is the clear candidate. `mondo_id` is required, unique, and validated to
  start with `MONDO:`. The only wrinkle is that Mondo terms can be obsoleted or merged;
  if that happens, the HCI record keeps its old Mondo ID, which is still a stable string
  even if it is no longer current.
- **Publication** mostly qualifies. PubMed publications have a unique `pubmed_id`;
  bioRxiv and medRxiv preprints have a unique `doi` and no PMID. The URL and label must
  therefore be "PMID if present, otherwise DOI". DOIs contain slashes, so they need the
  `path` URL converter or encoding. A preprint that is later published in a journal gets
  a PMID, which would change its URL; that case needs a redirect.
- **Allele** only partly qualifies. `car_id` is nullable (`get_car_id` returns `None`
  when the ClinGen Allele Registry has no match), so not every allele has one. The
  allele `name` (e.g., `DRB1*15:01`) is unique and meaningful, but contains `*` and `:`,
  which makes for awkward URLs. Dropping the `A` number requires either making `car_id`
  required or accepting the name as the URL key.
- **Haplotype, Curation, and Evidence** have no external IDs. They keep their HCI IDs.
  In particular, the `C` and `E` numbers are the public identifiers of published
  curations and must not change.

**What changes for a qualifying entity.** The detail, history, and change URLs use the
external ID instead of the slug (for diseases, `/disease/MONDO:0005052/detail`; the
colon is not allowed by Django's `slug` converter, so the pattern uses `str`). The ID
column in the list table and the "HCI ... ID" row on the detail page are removed, and
the external ID column becomes the link. `slug` is dropped from `search_fields`. Old
URLs keep working: a small view at the old pattern looks up the object by `slug` and
issues a permanent redirect to the new URL, so bookmarks and links in issues, emails,
and notes don't break.

**What stays.** The `slug` column stays in the database, the `save()` logic keeps
filling it in, and the repo JSON keeps its `slug` keys for now, so downstream consumers
of the published data aren't broken. Removing the column is a separate, later decision
that only makes sense once the JSON no longer exposes it and the redirects have been in
place long enough. Keeping the column costs nothing and keeps simple-history's
historical records readable.

**Impact.** The allele, disease, and publication pages are all behind
`ProtectedViewMixin`, so only logged-in curators have links to them; the public repo
pages link only by curation slug, which does not change. The public impact is limited
to the repo JSON, which this plan leaves alone. Tests that build URLs with slugs (e.g.,
`disease/tests.py` uses `"D000001"`) and templates that pass `object.slug` to
`{% url %}` need to change; switching those templates to `object.get_absolute_url`
removes most of the duplication. No data migration is needed for the URL and display
changes.

## Alternatives

**Drop the `slug` columns entirely.** This is the literal reading of "get rid of HCI
IDs". It requires schema migrations on the model and historical tables, breaks the repo
JSON, and makes redirects from old URLs impossible (nothing left to look them up by).
The benefit, one fewer column, is small. Not recommended until after the steps below.

**Use the external ID as the primary key.** Making `mondo_id` or `pubmed_id` the
primary key would mean rewriting every foreign key to those tables and would make
correcting a mistyped ID a cascading key change. Not recommended.

**Display-only change.** Keep all URLs as they are and only stop displaying the HCI ID
for diseases and publications. This is the cheapest option and gets most of the
user-visible benefit; it is Step 1 below and can stand alone if the URL change isn't
worth it.

## Open Questions

1. **Whether to do this at all, and for which entities.** The recommendation is
   Disease and Publication, and not Allele until `car_id` is guaranteed. This blocks
   every step.
2. **Display only, or URLs too?** Step 1 alone removes the visual noise; Steps 2-3
   change URLs and add redirects. This blocks Steps 2 and 3.
3. **Allele key.** If alleles are included, should the URL use the CAR ID (requiring
   `car_id` to be non-null for every allele, with a data check first) or the allele
   name? This blocks the allele variant of Step 3.
4. **Repo JSON.** Should the published JSON keep the `slug` keys indefinitely, or
   should they be deprecated and removed (with a version bump)? This blocks Step 4.

## Detailed Implementation

### Step 1 — Stop displaying HCI IDs for diseases and publications

#### `src/disease/tables.py`, `src/publication/tables.py` — modify

Remove the `slug` column from `DiseaseTable` and `PublicationTable`. Make `mondo_id`
(and, for publications, a PMID-or-DOI column) the `LinkColumn` to the detail page.

#### `src/disease/templates/disease/detail.html` — modify

Remove the HCI ID row from the detail table, and use the Mondo ID in the page title,
description, and breadcrumbs. Do the same in `disease/history.html` and
`disease/change.html`.

#### `src/publication/templates/publication/detail.html` — modify

Same change as for diseases, using the PMID or DOI, including `publication/history.html`
and `publication/change.html`.

#### `src/disease/models.py`, `src/publication/models.py` — modify

Add a `display_id` property: `mondo_id` for diseases; `f"PMID:{pubmed_id}"` or the DOI
for publications. Templates use it instead of `slug`.

#### `src/disease/tests.py`, `src/publication/tests/test_views.py` — modify

Tests first: the list and detail pages contain the Mondo ID or PMID and do not contain
the `D`/`P` slug; `display_id` returns the right value for PubMed and preprint
publications.

#### `src/disease/README.md`, `src/publication/README.md` — modify

Update the descriptions of the changed tables, models, and templates.

### Step 2 — Look up diseases and publications by external ID

#### `src/disease/urls.py`, `src/publication/urls.py` — modify

Change the detail, history, and change patterns to `<str:mondo_id>/...` for diseases
and `<path:publication_id>/...` for publications. Point `get_absolute_url` at the new
patterns.

#### `src/disease/views.py`, `src/publication/views.py` — modify

Set `slug_field = "mondo_id"` and `slug_url_kwarg = "mondo_id"` on the disease views.
For publications, override `get_object` to match `pubmed_id` when the value is all
digits and `doi` otherwise. Update `HistoryTable` construction so change links use the
external ID. Remove `slug` from `search_fields`.

#### Templates in both apps — modify

Replace `{% url '...-detail' object.slug %}` with `object.get_absolute_url` (or pass the
external ID) in the detail, history, and change templates.

#### `src/disease/tests.py`, `src/publication/tests/test_views.py` — modify

Tests first: reversing and resolving each URL with a Mondo ID, a PMID, and a DOI with
slashes; the history change link resolves.

#### `src/disease/README.md`, `src/publication/README.md` — modify

Describe the new URL patterns.

### Step 3 — Redirect old HCI ID URLs

#### `src/disease/urls.py`, `src/publication/urls.py` — modify

Keep the old `<slug:slug>/detail`, `/history`, and `/history/<int:history_id>/change`
patterns, pointing at a redirect view. Since `D000001` also matches `str`, put the
legacy patterns first with a regex (`re_path(r"^(?P<slug>D\d{6})/detail$", ...)`) so
they only catch HCI IDs.

#### `src/common/views.py` — modify

Add a `LegacySlugRedirectView(RedirectView)` with `permanent = True` that takes a
`model` attribute, looks the object up by `slug` (404 if missing), and redirects to
the object's new URL (preserving the history ID for change pages).

#### `src/common/tests.py` — modify

Unit-test `LegacySlugRedirectView` with a disease: redirect target and 404 behavior.

#### `src/disease/tests.py`, `src/publication/tests/test_views.py` — modify

Tests first: an old URL returns a 301 to the new one; an unknown slug returns 404.

#### `src/common/README.md` — modify

Describe the redirect view.

### Step 4 — Repo JSON (only if decided)

#### `src/repo/serializers.py` — modify

Depending on Open Question 4, either leave the `slug` keys alone, or remove them from
the disease and publication objects in `serialize_published_curation` and
`serialize_evidence` (they already include `mondo_id`, `pubmed_id`, and `doi`). If
removed, note it in the repo page and bump the export format.

#### `src/repo/tests.py` — modify

Update the serializer tests to match.

#### `src/repo/README.md` — modify

Describe the change.

## Sources

- Notes: "For entities with stable IDs, get rid of HCI IDs"
- https://github.com/ClinGen/hla-curation-interface/issues/77 (curators refer to
  curations by their "C number")
