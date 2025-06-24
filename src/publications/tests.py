"""Houses tests for the publications app."""

from bs4 import BeautifulSoup
from django.test import Client, TestCase
from django.urls import reverse


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
