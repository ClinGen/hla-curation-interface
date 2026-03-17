from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from django.test import TestCase
from django.urls import reverse

from common.tests import ProtectedViewTestMixin
from publication.models import Publication


class PublicationCreateTest(ProtectedViewTestMixin, TestCase):
    url = reverse("publication-create")
    template = "publication/create.html"
    page_name = "Add Publication"
    expected_text = [
        "Add Publication",
        "Publication Type",
        "PubMed Article",
        "bioRxiv Paper",
        "medRxiv Paper",
        "PubMed ID",
        "DOI",
        "Submit",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    @patch("publication.views.fetch_pubmed_data")
    def test_creates_pubmed_publication_with_valid_form_data(
        self, mock_fetch_pubmed_data: MagicMock
    ):
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "PUB", "pubmed_id": "123"}
        mock_pubmed_response = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <Article>
        <ArticleTitle>Common diseases in Pokémon</ArticleTitle>
        <AuthorList CompleteYN="Y">
          <Author ValidYN="Y">
            <LastName>Oak</LastName>
          </Author>
          <Author ValidYN="Y">
            <LastName>Birch</LastName>
          </Author>
        </AuthorList>
      </Article>
      <PubDate>
        <Year>1999</Year>
      </PubDate>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
        """
        mock_fetch_pubmed_data.return_value = BeautifulSoup(mock_pubmed_response, "xml")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "PUB")  # type: ignore[union-attr]
        self.assertEqual(new_publication.pubmed_id, "123")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Oak")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Common diseases in Pokémon")  # type: ignore[union-attr]
        self.assertEqual(new_publication.publication_year, 1999)  # type: ignore[union-attr]

    @patch("publication.views.fetch_rxiv_data")
    def test_creates_biorxiv_publication_with_valid_form_data(
        self, mock_fetch_rxiv_data: MagicMock
    ):
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "BIO", "doi": "10.1101/123"}
        mock_fetch_rxiv_data.return_value = {
            "collection": [
                {
                    "title": "Common diseases in Pokémon",
                    "authors": "Oak, P.; Birch, P.",
                    "date": "2020-05-15",
                }
            ]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "BIO")  # type: ignore[union-attr]
        self.assertEqual(new_publication.doi, "10.1101/123")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Oak, P.")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Common diseases in Pokémon")  # type: ignore[union-attr]
        self.assertEqual(new_publication.publication_year, 2020)  # type: ignore[union-attr]

    @patch("publication.views.fetch_rxiv_data")
    def test_creates_medrxiv_publication_with_valid_form_data(
        self, mock_fetch_rxiv_data: MagicMock
    ):
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "MED", "doi": "10.1101/456"}
        mock_fetch_rxiv_data.return_value = {
            "collection": [
                {
                    "title": "Diseases in Johto region Pokémon",
                    "authors": "Elm, P.; Juniper, P.",
                    "date": "2021-03-20",
                }
            ]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "MED")  # type: ignore[union-attr]
        self.assertEqual(new_publication.doi, "10.1101/456")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Elm, P.")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Diseases in Johto region Pokémon")  # type: ignore[union-attr]
        self.assertEqual(new_publication.publication_year, 2021)  # type: ignore[union-attr]

    def test_does_not_create_publication_with_invalid_form_data(self):
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": ""}  # The publication_type field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "publication/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("pubmed_id", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Publication.objects.count(), initial_publication_count)


class PublicationDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_publications.json"]
    url = reverse("publication-detail", kwargs={"slug": "P000001"})
    template = "publication/detail.html"
    page_name = "P000001 Details"
    expected_text = [
        "Diseases in grass type Pokémon in the Kanto region",
        "Oak",
        "123",
        "10.1000/123",
        "1990-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


class PublicationListTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_publications.json"]
    url = reverse("publication-list")
    template = "publication/list.html"
    page_name = "Publication Search"
    expected_text = [
        "ID",
        "Title",
        "Author",
        "Year",
        "PMID",
        "DOI",
        "Added",
        "P000001",
        "Diseases in grass type Pokémon in the Kanto region",
        "Oak",
        "123",
        "10.1000/123",
        "1990-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)
