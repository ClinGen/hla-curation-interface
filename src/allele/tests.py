from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import ProtectedViewTestMixin
from haplotype.models import Haplotype


class AlleleCreateTest(ProtectedViewTestMixin, TestCase):
    url = reverse("allele-create")
    template = "allele/create.html"
    page_name = "Add Allele"
    expected_text = ["Add Allele", "Name", "HLA allele"]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_shows_allele_name_input(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Name")

    def test_shows_submit_button(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Submit")

    @patch("allele.views.fetch_allele_data")
    def test_creates_allele_with_valid_form_data(
        self, mock_fetch_allele_data: MagicMock
    ):
        initial_allele_count = Allele.objects.count()
        data = {"name": "ASH*01:02:03"}
        mock_fetch_allele_data.return_value = [  # Mock the CAR API response.
            {
                "@id": "https://reg.clinicalgenome.org/allele/XAHLA123",
                "hlaFields": [
                    {
                        "alleleGroup": "01",
                        "descriptor": "ASH*01:02:03",
                        "gene": "ASH",
                        "hlaProtein": "02",
                        "synonDnaSub": "03",
                    }
                ],
                "id": "XAHLA123",
                "type": "hla",
            }
        ]
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Allele.objects.count(), initial_allele_count + 1)
        new_allele = Allele.objects.first()
        self.assertIsNotNone(new_allele)
        self.assertEqual(new_allele.name, "ASH*01:02:03")  # type: ignore[union-attr]
        self.assertEqual(new_allele.car_id, "XAHLA123")  # type: ignore[union-attr]
        self.assertEqual(new_allele.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]

    def test_does_not_create_allele_with_invalid_form_data(self):
        initial_allele_count = Allele.objects.count()
        data = {"name": ""}  # The name field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "allele/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Allele.objects.count(), initial_allele_count)


class AlleleDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json"]
    url = reverse("allele-detail", kwargs={"slug": "A000001"})
    template = "allele/detail.html"
    page_name = "A000001 Details"
    expected_text = ["A*01:02:03", "XAHLA123", "1970-01-01"]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_shows_car_registry_label(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ClinGen Allele Registry")

    def test_shows_haplotype(self):
        allele_1 = Allele.objects.get(pk=1)
        allele_2 = Allele.objects.get(pk=2)
        haplotype_name = allele_1.name + "~" + allele_2.name
        haplotype = Haplotype.objects.create(name=haplotype_name)
        haplotype.alleles.add(allele_1)
        haplotype.alleles.add(allele_2)
        response = self.client.get(self.url)
        self.assertContains(response, haplotype.slug)
        self.assertContains(response, haplotype_name)


class AlleleListTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json"]
    url = reverse("allele-list")
    template = "allele/list.html"
    page_name = "Allele Search"
    expected_text = [
        "ID",
        "Name",
        "CAR ID",
        "Added",
        "A000001",
        "A*01:02:03",
        "XAHLA123",
        "1970-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)
