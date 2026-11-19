from unittest.mock import MagicMock, patch
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import ProtectedViewTestMixin
from haplotype.constants.models import ALLELE_SEPARATORS
from haplotype.models import Haplotype


class HaplotypeCreateTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json"]
    url = reverse("haplotype-create")
    template = "haplotype/create.html"
    page_name = "Add Haplotype"
    expected_text = ["Add Haplotype", "Alleles", "separated by ~, spaces", "Submit"]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_creates_haplotype_from_typed_alleles_in_any_order(self):
        response = self.client.post(self.url, {"alleles": "B*04:05:06 A*01:02:03"})
        self.assertEqual(response.status_code, 302)
        haplotype = Haplotype.objects.get(name="A*01:02:03~B*04:05:06")
        self.assertEqual(
            set(haplotype.alleles.values_list("name", flat=True)),
            {"A*01:02:03", "B*04:05:06"},
        )
        self.assertEqual(haplotype.added_by, self.user4_yes_phi_yes_perms)

    def test_accepts_tildes_and_commas(self):
        for typed in ["A*01:02:03~B*04:05:06", "B*04:05:06, A*01:02:03"]:
            with self.subTest(typed=typed):
                response = self.client.post(self.url, {"alleles": typed})
                Haplotype.objects.all().delete()
                self.assertEqual(response.status_code, 302)

    def test_sorts_by_gene_position_not_alphabetically(self):
        response = self.client.post(
            self.url, {"alleles": "B*04:05:06 C*07:08:09"}
        )  # B is after C on chromosome 6.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Haplotype.objects.filter(name="C*07:08:09~B*04:05:06").exists())

    @patch("allele.models.fetch_allele_data")
    def test_unknown_allele_is_a_field_error_without_fetching(
        self, mock_fetch: MagicMock
    ):
        response = self.client.post(self.url, {"alleles": "A*01:02:03 DRB1*15:01"})
        self.assertEqual(response.status_code, 200)
        error = response.context["form"].errors["alleles"][0]
        self.assertIn("DRB1*15:01", error)
        self.assertContains(response, f'href="{reverse("allele-create")}"')
        self.assertFalse(Haplotype.objects.exists())
        mock_fetch.assert_not_called()

    def test_unknown_gene_returns_form_error(self):
        Allele.objects.create(name="ZZZ*01:01")
        response = self.client.post(self.url, {"alleles": "A*01:02:03 ZZZ*01:01"})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("ZZZ*01:01 has an unknown gene.", form.errors["alleles"])
        self.assertFalse(Haplotype.objects.exists())

    def test_duplicate_allele_combination_returns_form_error(self):
        self.client.post(self.url, {"alleles": "A*01:02:03 B*04:05:06"})
        response = self.client.post(self.url, {"alleles": "B*04:05:06~A*01:02:03"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("already exists", response.context["form"].errors["alleles"][0])
        self.assertEqual(Haplotype.objects.count(), 1)

    def test_requires_alleles(self):
        response = self.client.post(self.url, {"alleles": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(Haplotype.objects.exists())

    def test_alleles_input_suggests_the_allele_being_typed(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        alleles_input = soup.select_one('input[name="alleles"]')
        assert alleles_input is not None
        self.assertEqual(alleles_input["hx-get"], reverse("allele-suggest"))
        self.assertEqual(
            alleles_input["data-suggest-separators"], ALLELE_SEPARATORS.pattern
        )
        self.assertIsNone(soup.select_one("select"))


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

    @patch("allele.models.fetch_allele_data")
    def test_accepts_spaces_and_commas_between_alleles(self, mock_fetch: MagicMock):
        for typed in [
            "A*01:02:03 B*04:05:06",
            "B*04:05:06, A*01:02:03",
            "A*01:02:03,B*04:05:06",
            "B*04:05:06 ~ A*01:02:03",
            "A*01:02:03~~B*04:05:06",
        ]:
            with self.subTest(typed=typed):
                haplotype, _alleles = Haplotype.get_or_build(typed)
                self.assertEqual(haplotype, Haplotype.objects.get(pk=1))
        mock_fetch.assert_not_called()

    def test_raises_for_malformed_string(self):
        for typed in ["", " ", "A*01:02:03~", ", A*01:02:03"]:
            with (
                self.subTest(typed=typed),
                self.assertRaisesMessage(ValidationError, "spaces, or commas"),
            ):
                Haplotype.get_or_build(typed)

    def test_raises_for_unknown_gene(self):
        with self.assertRaisesMessage(ValidationError, "ZZZ"):
            Haplotype.get_or_build("A*01:02:03~ZZZ*01:01")

    @patch("allele.models.fetch_allele_data", return_value=None)
    def test_raises_when_allele_fetch_fails(self, _mock_fetch: MagicMock):
        with self.assertRaisesMessage(ValidationError, "ClinGen Allele Registry"):
            Haplotype.get_or_build("A*01:02:03~DRB1*15:01")


class HaplotypeSuggestTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]
    url = f"{reverse('haplotype-suggest')}?{urlencode({'q': 'b*04'})}"
    template = "common/partials/suggestions.html"
    page_name = "A*01:02:03~B*04:05:06"
    expected_text = ['data-value="A*01:02:03~B*04:05:06"']

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def _suggest(self, q: str) -> list[str]:
        response = self.client.get(reverse("haplotype-suggest"), {"q": q})
        return [value for value, _label in response.context["suggestions"]]

    def test_matches_every_part_in_any_order_with_any_separator(self):
        for q in ["b*04 a*01", "B*04, A*01", "B*04~A*01", "A*01:02:03~B*04:05:06"]:
            with self.subTest(q=q):
                self.assertEqual(self._suggest(q), ["A*01:02:03~B*04:05:06"])

    def test_needs_every_part_to_match(self):
        self.assertEqual(self._suggest("A*01 C*07"), [])

    def test_suggests_at_most_ten(self):
        Haplotype.objects.bulk_create(
            Haplotype(name=f"A*01:{n:02d}~B*08:01") for n in range(12)
        )
        self.assertEqual(len(self._suggest("B*08")), 10)
