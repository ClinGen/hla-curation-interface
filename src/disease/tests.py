"""Houses tests for the disease app."""

from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse

from common.tests import CreateTestMixin, ViewTestMixin
from disease.models import Disease


class DiseaseCreateTest(CreateTestMixin, TestCase):
    def setUp(self):
        self.url = reverse("disease-create")
        super().setUp()

    def test_shows_mondo_input(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Mondo")

    def test_shows_submit_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Submit")

    @patch("disease.views.fetch_disease_data")
    def test_creates_disease_with_valid_form_data(
        self, mock_fetch_disease_data: MagicMock
    ):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        initial_disease_count = Disease.objects.count()
        data = {"mondo_id": "MONDO:123"}
        mock_fetch_disease_data.return_value = {  # Mock the OLS API response.
            "_embedded": {
                "terms": [
                    {
                        "iri": "http://purl.obolibrary.org/obo/MONDO_123",
                        "label": "acute oran berry intoxication",
                    }
                ]
            }
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Disease.objects.count(), initial_disease_count + 1)
        new_disease = Disease.objects.first()
        self.assertIsNotNone(new_disease)
        self.assertEqual(new_disease.mondo_id, "MONDO:123")  # type: ignore[union-attr]
        self.assertEqual(new_disease.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]
        self.assertEqual(new_disease.name, "acute oran berry intoxication")  # type: ignore[union-attr]
        self.assertEqual(new_disease.iri, "http://purl.obolibrary.org/obo/MONDO_123")  # type: ignore[union-attr]

    def test_does_not_create_disease_with_invalid_form_data(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        initial_disease_count = Disease.objects.count()
        data = {"mondo_id": ""}  # The mondo_id field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "disease/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("mondo_id", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Disease.objects.count(), initial_disease_count)


class DiseaseDetailTest(ViewTestMixin, TestCase):
    fixtures = ["test_diseases.json"]
    url = reverse("disease-detail", kwargs={"slug": "D000001"})
    template = "disease/detail.html"
    page_name = "D000001 Details"
    expected_text = ["MONDO:123", "2000-01-01"]


class DiseaseListTest(ViewTestMixin, TestCase):
    fixtures = ["test_diseases.json"]
    url = reverse("disease-list")
    template = "disease/list.html"
    page_name = "Disease Search"
    expected_text = [
        "ID",
        "Name",
        "Mondo ID",
        "Added",
        "D000001",
        "acute oran berry intoxication",
        "MONDO:123",
        "2000-01-01",
    ]
