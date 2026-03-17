from django.test import TestCase
from django.urls import reverse

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
        self.assertIsNotNone(new_haplotype)
        self.assertEqual(new_haplotype.name, "A*01:02:03~B*04:05:06")  # type: ignore[union-attr]
        self.assertEqual(new_haplotype.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]

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
    expected_text = ["A*01:02:03~B*04:05:06", "1970-01-01", "A000001", "A000002"]

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
        "Added",
        "H000001",
        "A*01:02:03~B*04:05:06",
        "1970-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)
