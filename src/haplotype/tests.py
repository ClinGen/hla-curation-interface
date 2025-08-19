"""Houses tests for the haplotype app."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from haplotype.models import Haplotype


class HaplotypeCreateTest(TestCase):
    fixtures = ["test_alleles.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("haplotype-create")
        self.active_user = User.objects.create(
            username="ash",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        self.inactive_user = User.objects.create(
            username="misty",
            password="togepi",  # noqa: S106 (Hard-coded for testing.)
            is_active=False,
        )
        self.user_with_unverified_email = User.objects.create(
            username="brock",
            password="onix",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.user_with_unverified_email,
            firebase_email_verified=False,
        )
        self.user_who_can_create = User.objects.create(
            username="meowth",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.user_who_can_create,
            firebase_email_verified=True,
        )

    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_permission_denied_if_not_active(self):
        self.client.force_login(self.inactive_user)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_no_user_profile(self):
        self.client.force_login(self.active_user)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_email_not_verified(self):
        self.client.force_login(self.user_with_unverified_email)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_alleles_select_is_in_html(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        alleles_select = soup.find(id="id_alleles")
        self.assertIsNotNone(alleles_select)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    def test_creates_haplotype_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_haplotype_count = Haplotype.objects.count()
        data = {"alleles": ["1", "2"]}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Haplotype.objects.count(), initial_haplotype_count + 1)
        new_haplotype = Haplotype.objects.first()
        self.assertIsNotNone(new_haplotype)
        self.assertEqual(new_haplotype.name, "A*01:02:03~B*04:05:06")  # type: ignore[union-attr]
        self.assertEqual(new_haplotype.added_by, self.user_who_can_create)  # type: ignore[union-attr]

    def test_does_not_create_haplotype_with_invalid_form_data(self):
        self.client.force_login(self.user_who_can_create)
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


class HaplotypeDetailTest(TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("haplotype-detail", kwargs={"slug": "H000001"})

    def test_shows_haplotype_name(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_name = soup.find(id="haplotype-1-name").get_text().strip()
        self.assertEqual(allele_name, "A*01:02:03~B*04:05:06")

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="haplotype-1-added-at").get_text().strip()
        self.assertEqual(added_at, "1970-01-01")

    def test_shows_allele_ids(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_1_name = soup.find(id="allele-1-anchor").get_text().strip()
        self.assertIn("1", allele_1_name)
        allele_2_name = soup.find(id="allele-2-anchor").get_text().strip()
        self.assertIn("2", allele_2_name)

    def test_shows_allele_names(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_1_name = soup.find(id="allele-1-name").get_text().strip()
        self.assertEqual(allele_1_name, "A*01:02:03")
        allele_2_name = soup.find(id="allele-2-name").get_text().strip()
        self.assertEqual(allele_2_name, "B*04:05:06")


class HaplotypeSearchTest(TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("haplotype-search")

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_label = soup.find("label", {"for": "search-slug-input"}).get_text().strip()
        self.assertEqual(id_label, "ID")
        id_input = soup.find(id="search-slug-input")
        self.assertIsNotNone(id_input)

    def test_shows_haplotype_name_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_label = (
            soup.find("label", {"for": "search-haplotype-name-input"})
            .get_text()
            .strip()
        )
        self.assertEqual(name_label, "Name")
        name_input = soup.find(id="search-haplotype-name-input")
        self.assertIsNotNone(name_input)

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
        self.assertIn("H000001", id_anchor)

    def test_shows_haplotype_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[1].get_text().strip()
        self.assertIn("A*01:02:03~B*04:05:06", name)

    def test_shows_added_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        self.assertIn("1970-01-01", added_at)
