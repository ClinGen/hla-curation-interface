from io import StringIO
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from django.core.management import call_command
from django.test import TestCase

from publication.models import Publication
from publication.tests.test_views import MOCK_PUBMED_XML

COMMAND = "backfill_publication_authors"


@patch("publication.management.commands.backfill_publication_authors.time.sleep")
@patch("publication.clients.fetch_pubmed_data")
class BackfillPublicationAuthorsTest(TestCase):
    def setUp(self):
        self.empty = Publication.objects.create(pubmed_id="1", author="Old")
        self.filled = Publication.objects.create(
            pubmed_id="2", author="Elm", authors="Elm P; Rowan K"
        )

    def _run(self, *args: str) -> tuple[str, str]:
        out, err = StringIO(), StringIO()
        call_command(COMMAND, *args, stdout=out, stderr=err)
        return out.getvalue(), err.getvalue()

    def test_fills_publications_without_authors(
        self, mock_fetch: MagicMock, _mock_sleep: MagicMock
    ):
        mock_fetch.return_value = BeautifulSoup(MOCK_PUBMED_XML, "xml")
        out, _ = self._run()
        self.empty.refresh_from_db()
        self.assertEqual(self.empty.authors, "Oak; Birch")
        self.assertEqual(self.empty.author, "Oak")
        self.assertIn("Updated 1", out)

    def test_leaves_publications_with_authors_untouched(
        self, mock_fetch: MagicMock, _mock_sleep: MagicMock
    ):
        mock_fetch.return_value = BeautifulSoup(MOCK_PUBMED_XML, "xml")
        self._run()
        mock_fetch.assert_called_once_with(self.empty.pubmed_id)
        self.filled.refresh_from_db()
        self.assertEqual(self.filled.authors, "Elm P; Rowan K")

    def test_dry_run_writes_nothing_and_skips_pubmed(
        self, mock_fetch: MagicMock, _mock_sleep: MagicMock
    ):
        out, _ = self._run("--dry-run")
        mock_fetch.assert_not_called()
        self.empty.refresh_from_db()
        self.assertEqual(self.empty.authors, "")
        self.assertIn(self.empty.slug, out)
        self.assertNotIn(self.filled.slug, out)

    def test_logs_a_failure_and_keeps_going(
        self, mock_fetch: MagicMock, mock_sleep: MagicMock
    ):
        second = Publication.objects.create(pubmed_id="3")
        mock_fetch.side_effect = [None, BeautifulSoup(MOCK_PUBMED_XML, "xml")]
        with self.assertLogs(
            "publication.management.commands.backfill_publication_authors",
            level="WARNING",
        ):
            out, err = self._run()
        self.empty.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(self.empty.authors, "")
        self.assertEqual(second.authors, "Oak; Birch")
        self.assertIn(self.empty.slug, err)
        self.assertIn("Updated 1", out)
        self.assertIn("failed 1", out)
        # It waits between requests, not before the first one.
        self.assertEqual(mock_sleep.call_count, 1)
