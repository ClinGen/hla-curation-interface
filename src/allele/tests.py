"""Houses tests for the allele app."""

from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import CreateTestMixin
from haplotype.models import Haplotype


class AlleleCreateTest(CreateTestMixin, TestCase):
    def setUp(self):
        self.url = reverse("allele-create")
        super().setUp()

    def test_shows_allele_name_input(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_name = soup.find(id="id_name")
        self.assertIsNotNone(allele_name)

    def test_shows_submit_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    @patch("allele.views.fetch_allele_data")
    def test_creates_allele_with_valid_form_data(
        self, mock_fetch_allele_data: MagicMock
    ):
        self.client.force_login(self.user4_yes_phi_yes_perms)
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
        self.client.force_login(self.user4_yes_phi_yes_perms)
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


class AlleleDetailTest(TestCase):
    fixtures = ["test_alleles.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("allele-detail", kwargs={"slug": "A000001"})

    def test_shows_car_logo(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_logo = soup.find("img", {"class": "entity-type-logo"})
        self.assertIn("ClinGen Allele Registry", car_logo.attrs["alt"])

    def test_shows_allele_name(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_name = soup.find(id="allele-1-name").get_text().strip()
        self.assertEqual(allele_name, "A*01:02:03")

    def test_shows_car_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_id = soup.find(id="allele-1-car-id").get_text().strip()
        self.assertEqual(car_id, "XAHLA123")

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="allele-1-added-at").get_text().strip()
        self.assertEqual(added_at, "1970-01-01")

    def test_shows_search_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        search_button = soup.find(id="search-button").get_text().strip()
        self.assertIn("Search", search_button)

    def test_shows_add_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_button = soup.find(id="add-button").get_text().strip()
        self.assertIn("Add", add_button)

    def test_shows_haplotype(self):
        allele_1 = Allele.objects.get(pk=1)
        allele_2 = Allele.objects.get(pk=2)
        haplotype_name = allele_1.name + "~" + allele_2.name
        haplotype = Haplotype.objects.create(name=haplotype_name)
        haplotype.alleles.add(allele_1)
        haplotype.alleles.add(allele_2)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        haplotype_anchor = soup.find(id="haplotype-anchor").get_text().strip()
        self.assertIn(str(haplotype.pk), haplotype_anchor)
        haplotype_name_in_html = soup.find(id="haplotype-name").get_text().strip()
        self.assertEqual(haplotype_name_in_html, haplotype_name)


class AlleleSearchTest(TestCase):
    fixtures = ["test_alleles.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("allele-search")

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_label = soup.find("label", {"for": "search-slug-input"}).get_text().strip()
        self.assertEqual(id_label, "ID")
        id_input = soup.find(id="search-slug-input")
        self.assertIsNotNone(id_input)

    def test_shows_allele_name_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_label = (
            soup.find("label", {"for": "search-allele-name-input"}).get_text().strip()
        )
        self.assertEqual(name_label, "Name")
        name_input = soup.find(id="search-allele-name-input")
        self.assertIsNotNone(name_input)

    def test_shows_car_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_id_label = (
            soup.find("label", {"for": "search-car-id-input"}).get_text().strip()
        )
        self.assertIsNotNone(car_id_label, "CAR ID")
        car_id_input = soup.find(id="search-car-id-input")
        self.assertIsNotNone(car_id_input)

    def test_shows_added_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_label = (
            soup.find("label", {"for": "sort-added-at-button"}).get_text().strip()
        )
        self.assertEqual(added_label, "Added")
        added_button = soup.find(id="sort-added-at-button")
        self.assertIsNotNone(added_button)

    def test_shows_id_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_anchor = (
            soup.find("tbody").find("tr").find_all("td")[0].find("a").get_text().strip()
        )
        self.assertIn("A000001", id_anchor)

    def test_shows_allele_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[1].get_text().strip()
        self.assertIn("A*01:02:03", name)

    def test_shows_car_id_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_id = (
            soup.find("tbody").find("tr").find_all("td")[2].find("a").get_text().strip()
        )
        self.assertIn("XAHLA123", car_id)

    def test_shows_added_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find("tbody").find("tr").find_all("td")[3].get_text().strip()
        self.assertIn("1970-01-01", added_at)
