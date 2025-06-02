"""Houses tests for the core app."""

from django.test import Client, TestCase
from django.urls import reverse


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("home")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "HLA Curation Interface")


class AboutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("about")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "About")
        self.assertContains(response, "HLA Curation Interface (HCI)")
        self.assertContains(response, "alleles")
        self.assertContains(response, "haplotypes")
        self.assertContains(response, "Stanford University")


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("contact")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Contact")
        self.assertContains(response, "email")
        self.assertContains(response, "helpdesk@clinicalgenome.org")


class HelpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("help")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Help")
        self.assertContains(response, "user documentation")
        self.assertContains(response, "email")
        self.assertContains(response, "helpdesk@clinicalgenome.org")


class DownloadsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("downloads")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Downloads")
        self.assertContains(response, "CC BY-SA 4.0")
        self.assertContains(response, "CSV")
        self.assertContains(response, "JSON")


class CitingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("citing")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Citing")
        self.assertContains(response, "format")
        self.assertContains(response, "dataset")


class AcknowledgementsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("acknowledgements")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Acknowledgements")
        self.assertContains(response, "NIH/NHGRI")
        self.assertContains(response, "Steven Mack")


class CollaboratorsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("collaborators")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Collaborators")
        self.assertContains(response, "The Baylor College of Medicine ClinGen Team")
        self.assertContains(response, "PharmGKB")
