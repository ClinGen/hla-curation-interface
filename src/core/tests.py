"""Houses tests for the core app."""

from django.test import Client, TestCase
from django.urls import reverse


class HomeViewTest(TestCase):
    """Tests the home view."""

    def setUp(self):
        """Sets up the mock browser and the URL for the tests."""
        self.client = Client()
        self.url = reverse("home")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
