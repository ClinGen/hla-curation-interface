# Store All Publication Authors and Search on Them

## The Problem

When a curator adds a publication, `PublicationCreate.form_valid`
(`src/publication/views.py`) calls `get_pubmed_author` (`src/publication/clients.py`),
which stores only the surname of the first author. It does this with
`soup.find("LastName")`, which returns the first `<LastName>` anywhere in the PubMed
XML. `Publication.author` (`src/publication/models.py`) is a `CharField` with
`max_length=16` that holds that one surname. The publication search (`PublicationList`,
a `SearchListView` with `search_fields = ["slug", "title", "author", "doi",
"pubmed_id"]`) can therefore only find a paper by its primary author. Curators often
know a paper by a senior or middle author (for example, "Mack" for PMID 38226399, whose
first author is Noble), so they can't find it.

The goal is to store the full, ordered author list for each publication, show it on the
publication detail page, and let the publication search match any author.

When issue #27 was written, this had to cover PubMed, bioRxiv, and medRxiv. Once ticket
001 removes preprints from Add Publication, PubMed is the only source of new
publications. This ticket therefore only fetches authors from PubMed. Legacy preprint
rows keep their single `author` value.

## The Technical Plan

Add an `authors` text field to `Publication` that stores the author list in PubMed order
as a single `"; "`-joined string, for example `"Noble JA; Besançon S; ...; Mack SJ"`. A
new client function, `get_pubmed_authors`, reads
`MedlineCitation/Article/AuthorList/Author` from the efetch XML. For each `Author`, it
emits `"LastName Initials"`, or the `CollectiveName` for group authors.
`PublicationCreate` fills `authors` alongside the existing fields. Adding `"authors"` to
`PublicationList.search_fields` is enough to make the existing search box match any
author, because `SearchListView.get_queryset` ORs `icontains` filters across all search
fields. The existing `author` field stays as the primary author and is still shown in
the `PublicationTable` "Author" column.

Existing publications have an empty `authors` value. A management command backfills it
by re-fetching each PubMed publication.

## Alternatives

**An `Author` model with a many-to-many relation.** This would be normalized and would
support per-author pages or disambiguation. The HCI only needs to display and search
author names, though, and a text field does that with no joins, no new admin, and a
one-line search change.

**A dedicated "Author" search input.** Issue #27 says "provide a search field". Adding
`authors` to the existing single search box meets that need without a second input and
without changing `SearchListView`. See Open Question 1.

## Open Questions

1. Is it acceptable for the existing single search box to also match authors, or does
   the curation team want a separate author-only search field? Recommendation: use the
   single box. A separate field would need `SearchListView` to support per-field query
   parameters. This blocks Step 3.
2. Should existing publications be backfilled from PubMed, and who runs the command in
   production? This blocks Step 4.

## Detailed Implementation

### Step 1 — Parse all authors from PubMed

#### `src/publication/tests/test_clients_unit.py` — create

Add offline unit tests (no network) that build a `BeautifulSoup(..., "xml")` from inline
XML and cover these cases for `get_pubmed_authors`: several authors returned in order as
`"LastName Initials"`; an `Author` with only `CollectiveName`; no `AuthorList` returns
`[]` and logs a warning; a `<LastName>` outside `AuthorList` (for example, in
`CommentsCorrectionsList`) is ignored. Also add a test that `get_pubmed_author` returns
the first `AuthorList` author's surname even when a `<LastName>` appears earlier in the
document.

#### `src/publication/clients.py` — modify

Add `get_pubmed_authors(soup: BeautifulSoup) -> list[str]` with a Google docstring.
Change `get_pubmed_author` so that it reads the first author from the same `AuthorList`
lookup instead of the first `LastName` anywhere in the document.

#### `src/publication/tests/test_clients.py` — modify

Add an `expected_authors_contains` entry to each `PUBMED_TEST_CASES` case (for example,
`"Mack SJ"` for 38226399). Add `test_get_pubmed_authors_extracts_authors` to
`PubMedContractTest`.

#### `src/publication/README.md` — modify

Update the `clients.py` and `tests/test_clients.py` entries, and add an entry for
`tests/test_clients_unit.py`.

### Step 2 — Store and display authors

#### `src/publication/models.py` — modify

Add `authors = models.TextField(blank=True, default="", verbose_name="Authors",
help_text="All authors of the publication, in order, separated by semicolons.")`.
Generate the migration with `just django-makemigrations`. The
migration also covers `HistoricalPublication`.

#### `src/publication/views.py` — modify

In `PublicationCreate.form_valid`, set `form.instance.authors =
"; ".join(get_pubmed_authors(pubmed_data))`.

#### `src/publication/templates/publication/detail.html` — modify

Add an "Authors" row after "Primary Author" that shows `object.authors` or "------".

#### `src/publication/tests/test_views.py` — modify

Write these tests first. The mocked PubMed response in
`test_creates_pubmed_publication_with_valid_form_data` already has two authors (Oak,
Birch), so assert that `new_publication.authors` contains both. In
`PublicationDetailTest`, add a fixture value and assert that the detail page shows it.

#### `src/publication/fixtures/test_publications.json` — modify

Add an `authors` value to the PubMed row (pk 1), for example `"Oak S; Juniper N"`.

#### `src/publication/README.md` — modify

Update the `models.py`, `views.py`, `templates/publication/detail.html`, and fixture
entries.

### Step 3 — Search by any author (blocked by Open Question 1)

#### `src/publication/views.py` — modify

Add `"authors"` to `PublicationList.search_fields`.

#### `src/publication/tests/test_views.py` — modify

Write this test first. In `PublicationListTest`, a GET with `?q=Juniper` (a non-primary
author from the fixture) returns P000001, and `?q=zzz_no_match` does not.

#### `src/publication/README.md` — modify

Update the `views.py` entry to say that search covers all authors.

### Step 4 — Backfill existing publications (blocked by Open Question 2)

#### `src/publication/management/commands/__init__.py` — create

This is an empty package marker. Also create an empty
`src/publication/management/__init__.py`.

#### `src/publication/management/commands/backfill_publication_authors.py` — create

This management command loops over `Publication.objects.filter(publication_type="PUB",
authors="")`. For each one, it calls `fetch_pubmed_data`, then `get_pubmed_authors`, and
saves with `update_fields=["authors"]`. It sleeps between requests to stay under NCBI's
limit (10 requests/second with `PUBMED_API_KEY`, 3 without), logs failures, and supports
`--dry-run`. Write tests first in `src/publication/tests/test_commands.py` with
`fetch_pubmed_data` mocked: rows get filled, rows that already have authors are
untouched, and `--dry-run` writes nothing.

#### `src/publication/README.md`, `docs/how-to.md` — modify

Add README entries for the new files, and add a how-to entry for running the command in
production.

## Sources

- https://github.com/ClinGen/hla-curation-interface/issues/27
- Notes: "HCI: Get all authors of a publication"
