from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import ProtectedViewTestMixin
from haplotype.models import Haplotype


class HaplotypeCreateTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json"]
    url = reverse("haplotype-create")
    template = "haplotype/create.html"
    page_name = "Add Haplotype"
    expected_text = ["Add Haplotype", "constituent alleles", "Submit"]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_alleles_select_is_in_html(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Alleles")

    def test_shows_submit_button(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Submit")

    def test_creates_haplotype_with_valid_form_data(self):
        initial_haplotype_count = Haplotype.objects.count()
        data = {"alleles": ["1", "2"]}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count + 1)
        new_haplotype = Haplotype.objects.first()
        assert new_haplotype is not None
        self.assertEqual(new_haplotype.name, "A*01:02:03~B*04:05:06")
        self.assertEqual(new_haplotype.added_by, self.user4_yes_phi_yes_perms)

    def test_reversed_allele_order_produces_same_sorted_name(self):
        initial_haplotype_count = Haplotype.objects.count()
        data = {"alleles": ["2", "1"]}  # B*04:05:06 before A*01:02:03
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count + 1)
        new_haplotype = Haplotype.objects.first()
        assert new_haplotype is not None
        self.assertEqual(new_haplotype.name, "A*01:02:03~B*04:05:06")

    def test_sorts_by_gene_position_not_alphabetically(self):
        data = {"alleles": ["2", "3"]}  # B is after C on chromosome 6.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Haplotype.objects.filter(name="C*07:08:09~B*04:05:06").exists())

    def test_unknown_gene_returns_form_error(self):
        unknown = Allele.objects.create(name="ZZZ*01:01")
        initial_haplotype_count = Haplotype.objects.count()
        response = self.client.post(self.url, {"alleles": ["1", str(unknown.pk)]})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("ZZZ*01:01 has an unknown gene.", form.errors["alleles"])
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count)

    def test_duplicate_allele_combination_returns_form_error(self):
        self.client.post(self.url, {"alleles": ["1", "2"]})
        initial_haplotype_count = Haplotype.objects.count()
        response = self.client.post(self.url, {"alleles": ["2", "1"]})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "haplotype/create.html")
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("alleles", form.errors)
        self.assertIn("already exists", form.errors["alleles"][0])
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count)

    def test_does_not_create_haplotype_with_invalid_form_data(self):
        initial_haplotype_count = Haplotype.objects.count()
        data = {"alleles": []}  # The alleles field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "haplotype/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("alleles", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count)


class HaplotypeDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]
    url = reverse("haplotype-detail", kwargs={"slug": "H000001"})
    template = "haplotype/detail.html"
    page_name = "H000001 Details"
    expected_text = [
        "HLA-A*01:02:03~HLA-B*04:05:06",
        "1970-01-01",
        "A000001",
        "A000002",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


class HaplotypeListTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]
    url = reverse("haplotype-list")
    template = "haplotype/list.html"
    page_name = "Haplotype Search"
    expected_text = [
        "ID",
        "Name",
        "Updated",
        "H000001",
        "HLA-A*01:02:03~HLA-B*04:05:06",
        "1970-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


class HaplotypeCanonicalNameTest(TestCase):
    def test_sorts_alleles_by_gene_position(self):
        name = Haplotype.canonical_name(["DQB1*06:02", "A*01:01", "DRB1*15:01"])
        self.assertEqual(name, "A*01:01~DRB1*15:01~DQB1*06:02")

    def test_raises_for_unknown_gene(self):
        with self.assertRaisesMessage(ValidationError, "ZZZ"):
            Haplotype.canonical_name(["A*01:01", "ZZZ*01:01"])


class HaplotypeGetOrBuildTest(TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]

    @patch("allele.models.fetch_allele_data")
    def test_returns_existing_haplotype_typed_out_of_order(self, mock_fetch: MagicMock):
        haplotype, alleles = Haplotype.get_or_build(" B*04:05:06 ~ A*01:02:03 ")
        self.assertEqual(haplotype, Haplotype.objects.get(pk=1))
        self.assertEqual(
            [allele.name for allele in alleles], ["A*01:02:03", "B*04:05:06"]
        )
        mock_fetch.assert_not_called()

    @patch(
        "allele.models.fetch_allele_data",
        return_value=[{"id": "XAHLA999", "type": "hla"}],
    )
    def test_builds_unsaved_haplotype_and_fetches_missing_allele(
        self, mock_fetch: MagicMock
    ):
        haplotype, alleles = Haplotype.get_or_build("DRB1*15:01~A*01:02:03")
        self.assertIsNone(haplotype.pk)
        self.assertEqual(haplotype.name, "A*01:02:03~DRB1*15:01")
        self.assertEqual(alleles[0], Allele.objects.get(name="A*01:02:03"))
        self.assertIsNone(alleles[1].pk)
        self.assertEqual(alleles[1].car_id, "XAHLA999")
        mock_fetch.assert_called_once_with("DRB1*15:01")

    def test_raises_for_malformed_string(self):
        for typed in ["", "A*01:02:03~", "A*01:02:03~~B*04:05:06"]:
            with self.subTest(typed=typed), self.assertRaises(ValidationError):
                Haplotype.get_or_build(typed)

    def test_raises_for_unknown_gene(self):
        with self.assertRaisesMessage(ValidationError, "ZZZ"):
            Haplotype.get_or_build("A*01:02:03~ZZZ*01:01")

    @patch("allele.models.fetch_allele_data", return_value=None)
    def test_raises_when_allele_fetch_fails(self, _mock_fetch: MagicMock):
        with self.assertRaisesMessage(ValidationError, "ClinGen Allele Registry"):
            Haplotype.get_or_build("A*01:02:03~DRB1*15:01")
