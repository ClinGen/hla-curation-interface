"""Offline unit tests for the PubMed client's parsers, using inline XML."""

from bs4 import BeautifulSoup
from django.test import SimpleTestCase

from publication.clients import get_pubmed_author, get_pubmed_authors


def _soup(author_list: str, extra: str = "", before: str = "") -> BeautifulSoup:
    xml = f"""<?xml version="1.0" ?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          {before}
          <Article>
            <ArticleTitle>A title.</ArticleTitle>
            {author_list}
          </Article>
          {extra}
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>"""
    return BeautifulSoup(xml, "xml")


def _author(last_name: str, initials: str) -> str:
    return (
        f"<Author><LastName>{last_name}</LastName>"
        f"<ForeName>Unused</ForeName><Initials>{initials}</Initials></Author>"
    )


# A LastName outside AuthorList, which the parsers must ignore.
STRAY_LAST_NAME = (
    "<CommentsCorrectionsList><CommentsCorrections><Author>"
    "<LastName>Stray</LastName></Author></CommentsCorrections>"
    "</CommentsCorrectionsList>"
)


class GetPubMedAuthorsTest(SimpleTestCase):
    def test_lists_authors_in_order(self):
        soup = _soup(
            "<AuthorList>"
            + _author("Noble", "JA")
            + _author("Besançon", "S")
            + _author("Mack", "SJ")
            + "</AuthorList>"
        )
        self.assertEqual(
            get_pubmed_authors(soup), ["Noble JA", "Besançon S", "Mack SJ"]
        )

    def test_uses_collective_name_for_group_authors(self):
        soup = _soup(
            "<AuthorList>"
            + _author("Noble", "JA")
            + "<Author><CollectiveName>T1D Consortium</CollectiveName></Author>"
            + "</AuthorList>"
        )
        self.assertEqual(get_pubmed_authors(soup), ["Noble JA", "T1D Consortium"])

    def test_author_without_initials_is_last_name_only(self):
        soup = _soup(
            "<AuthorList><Author><LastName>Noble</LastName></Author></AuthorList>"
        )
        self.assertEqual(get_pubmed_authors(soup), ["Noble"])

    def test_no_author_list_returns_empty_and_warns(self):
        with self.assertLogs("publication.clients", level="WARNING"):
            self.assertEqual(get_pubmed_authors(_soup("")), [])

    def test_ignores_last_name_outside_author_list(self):
        soup = _soup(
            "<AuthorList>" + _author("Noble", "JA") + "</AuthorList>",
            extra=STRAY_LAST_NAME,
        )
        self.assertEqual(get_pubmed_authors(soup), ["Noble JA"])


class GetPubMedAuthorTest(SimpleTestCase):
    def test_uses_first_author_in_author_list(self):
        # The stray LastName comes first, so soup.find("LastName") would pick it.
        soup = _soup(
            "<AuthorList>" + _author("Noble", "JA") + "</AuthorList>",
            before=STRAY_LAST_NAME,
        )
        self.assertEqual(get_pubmed_author(soup), "Noble")

    def test_skips_group_authors(self):
        # Publication.author holds a surname, so a leading group author is skipped.
        soup = _soup(
            "<AuthorList><Author><CollectiveName>T1D Consortium</CollectiveName>"
            "</Author>" + _author("Noble", "JA") + "</AuthorList>"
        )
        self.assertEqual(get_pubmed_author(soup), "Noble")

    def test_no_author_list_returns_empty_and_warns(self):
        with self.assertLogs("publication.clients", level="WARNING"):
            self.assertEqual(get_pubmed_author(_soup("")), "")
