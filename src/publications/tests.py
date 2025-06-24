"""Houses tests for the publications app."""

from django.test import Client, TestCase
from django.urls import reverse


class PublicationCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("publication-create")

    def test_shows_radio_buttons(self):
        self.client.get(self.url)
