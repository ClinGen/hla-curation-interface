"""Houses tests for the auth app."""

from django.test import Client, TestCase
from django.urls import reverse


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("woslogin")

    def test_redirects_to_workos(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class CallbackTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("woscallback")

    def test_redirects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
