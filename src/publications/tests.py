"""Houses tests for the publications app."""

from bs4 import BeautifulSoup
from django.db.models import DateTimeField
from django.test import Client, TestCase
from django.urls import reverse

from publications.models import Publication, PublicationTypes


class PublicationCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("publication-create")

    def test_shows_radio_buttons(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_radio = (
            soup.find("label", {"for": "id_publication_type_0"}).get_text().strip()
        )
        self.assertIn("PubMed", pubmed_radio)
        biorxiv_radio = (
            soup.find("label", {"for": "id_publication_type_1"}).get_text().strip()
        )
        self.assertIn("bioRxiv", biorxiv_radio)
        medrxiv_radio = (
            soup.find("label", {"for": "id_publication_type_2"}).get_text().strip()
        )
        self.assertIn("medRxiv", medrxiv_radio)

    def test_shows_inputs(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_input = soup.find(id="id_pubmed_id")
        self.assertIsNotNone(pubmed_input)
        doi_input = soup.find(id="id_doi")
        self.assertIsNotNone(doi_input)

    def test_shows_submit_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")


class PublicationDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.publication_type = PublicationTypes.PUBMED
        self.pubmed_id = "123"
        self.doi = "10.1000/182"
        self.title = "Common diseases in Pokémon"
        self.author = "Oak"
        self.added_at = DateTimeField(auto_now_add=True)
        self.publication = Publication.objects.create(
            publication_type=PublicationTypes.PUBMED,
            pubmed_id=self.pubmed_id,
            doi=self.doi,
            title=self.title,
            author=self.author,
            added_at=self.added_at,
        )
        self.url = reverse("publication-detail", kwargs={"pk": self.publication.pk})

    def test_shows_publication_type(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        publication_type_image = soup.find("img", {"class": "publication-logo"})
        self.assertIn("PubMed", publication_type_image.attrs["alt"])

    def test_shows_title(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find(id="publication-title").get_text().strip()
        self.assertEqual(self.title, title)

    def test_shows_author(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find(id="publication-title").get_text().strip()
        self.assertEqual(self.title, title)

    def test_shows_pubmed_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_id = soup.find(id="pubmed-id").find("a").get_text().strip()
        self.assertEqual(self.pubmed_id, pubmed_id)

    def test_shows_doi(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        doi = soup.find(id="doi").find("a").get_text().strip()
        self.assertEqual(self.doi, doi)

    def test_shows_date(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        date = soup.find(id="added-at").get_text().strip()
        self.assertIsNotNone(date)

    def test_shows_search_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        search_button = soup.find(id="search-button").get_text().strip()
        self.assertIn("Search", search_button)

    def test_shows_add_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_button = soup.find(id="add-button").get_text().strip()
        self.assertIn("Add", add_button)
