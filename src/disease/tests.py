"""Houses tests for the disease app."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from disease.models import Disease, DiseaseTypes


class DiseaseCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("disease-create")
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

    def test_shows_mondo_input(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        mondo_input = soup.find(id="id_mondo_id")
        self.assertIsNotNone(mondo_input)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    def test_creates_disease_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_disease_count = Disease.objects.count()
        data = {"mondo_id": "MONDO:123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Disease.objects.count(), initial_disease_count + 1)
        new_disease = Disease.objects.first()
        self.assertEqual(new_disease.mondo_id, "MONDO:123")
        self.assertEqual(new_disease.added_by, self.user_who_can_create)

    def test_does_not_create_disease_with_invalid_form_data(self):
        self.client.force_login(self.user_who_can_create)
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


class DiseaseDetailTest(TestCase):
    fixtures = ["disease.json"]

    def setUp(self):
        self.client = Client()
        self.disease_type = DiseaseTypes.MONDO
        self.url = reverse("disease-detail", kwargs={"pk": 1})

    def test_shows_disease_type(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        disease_type_image = soup.find("img", {"class": "entity-type-logo"})
        self.assertIn("Mondo", disease_type_image.attrs["alt"])

    def test_shows_mondo_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        mondo_id = soup.find(id="mondo-id").get_text().strip()
        self.assertEqual(mondo_id, "MONDO:123")

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="added-at").get_text().strip()
        self.assertEqual(added_at, "2000-01-01")

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


class DiseaseSearchTest(TestCase):
    fixtures = ["disease.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("disease-search")

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_label = soup.find("label", {"for": "search-pk-input"}).get_text().strip()
        self.assertEqual(id_label, "ID")
        id_input = soup.find(id="search-pk-input")
        self.assertIsNotNone(id_input)

    def test_shows_mondo_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        mondo_id_label = (
            soup.find("label", {"for": "search-mondo-id-input"}).get_text().strip()
        )
        self.assertEqual(mondo_id_label, "Mondo ID")
        mondo_id_input = soup.find(id="search-mondo-id-input")
        self.assertIsNotNone(mondo_id_input)

    def test_shows_name_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_label = (
            soup.find("label", {"for": "search-disease-name-input"}).get_text().strip()
        )
        self.assertEqual(name_label, "Name")
        name_input = soup.find(id="search-disease-name-input")
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
        self.assertIn("1", id_anchor)

    def test_shows_mondo_id_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        mondo_id_anchor = (
            soup.find("tbody").find("tr").find_all("td")[1].find("a").get_text().strip()
        )
        self.assertEqual("MONDO:123", mondo_id_anchor)

    def test_shows_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        self.assertEqual(name, "acute oran berry intoxication")

    def test_shows_added_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find("tbody").find("tr").find_all("td")[3].get_text().strip()
        self.assertIn("2000-01-01", added_at)
