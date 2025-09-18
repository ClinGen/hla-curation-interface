"""Houses tests for the repo app."""

from django.test import Client, TestCase
from django.urls import reverse


class RepoHomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("repo-home")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "HLARepo")
        self.assertContains(response, "under construction")
