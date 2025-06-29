"""Houses tests for the allele app."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from core.models import UserProfile


class AlleleCreateView(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("allele-create")
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

    def test_shows_allele_name_input(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_name = soup.find(id="id_name")
        self.assertIsNotNone(allele_name)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    def test_creates_allele_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_allele_count = Allele.objects.count()
        data = {"name": "ASH*01:02:03"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Allele.objects.count(), initial_allele_count + 1)
        new_allele = Allele.objects.first()
        self.assertEqual(new_allele.name, "ASH*01:02:03")
        self.assertEqual(new_allele.added_by, self.user_who_can_create)

    def test_does_not_create_allele_with_invalid_form_data(self):
        self.client.force_login(self.user_who_can_create)
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


class AlleleDetailView(TestCase):
    fixtures = ["allele.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("allele-detail", kwargs={"pk": 1})

    def test_shows_car_logo(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_logo = soup.find("img", {"class": "entity-type-logo"})
        self.assertIn("ClinGen Allele Registry", car_logo.attrs["alt"])

    def test_shows_allele_name(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_name = soup.find(id="allele-name").get_text().strip()
        self.assertEqual(allele_name, "FOO*01:02:03")

    def test_shows_car_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        car_id = soup.find(id="car-id").get_text().strip()
        self.assertEqual(car_id, "XAHLA123")

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="added-at").get_text().strip()
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


class SearchAlleleViewTest(TestCase):
    fixtures = ["allele.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("allele-search")

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_label = soup.find("label", {"for": "search-pk-input"}).get_text().strip()
        self.assertEqual(id_label, "ID")
        id_input = soup.find(id="search-pk-input")
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
        self.assertIn("1", id_anchor)

    def test_shows_allele_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[1].get_text().strip()
        self.assertIn("FOO*01:02:03", name)

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
