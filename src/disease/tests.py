"""Houses tests for the disease app."""

import datetime

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from disease.models import Disease, DiseaseTypes


class DiseaseCreateView(TestCase):
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
        pubmed_input = soup.find(id="id_mondo_id")
        self.assertIsNotNone(pubmed_input)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")


class DiseaseDetailView(TestCase):
    def setUp(self):
        self.client = Client()
        self.disease_type = DiseaseTypes.MONDO
        self.mondo_id = "MONDO:123"
        self.ols_iri = "http://purl.obolibrary.org/obo/MONDO_123"
        self.name = "acute oran berry intoxication"
        self.added_at = datetime.datetime.now(tz=datetime.UTC).date().isoformat()
        self.disease = Disease.objects.create(
            disease_type=self.disease_type,
            mondo_id=self.mondo_id,
            ols_iri=self.ols_iri,
            name=self.name,
            added_at=self.added_at,
        )
        self.url = reverse("disease-detail", kwargs={"pk": self.disease.pk})

    def test_shows_disease_type(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        disease_type_image = soup.find("img", {"class": "entity-type-logo"})
        self.assertIn("Mondo", disease_type_image.attrs["alt"])

    def test_shows_mondo_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        mondo_id = soup.find(id="mondo-id").get_text().strip()
        self.assertEqual(self.mondo_id, mondo_id)

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="added-at").get_text().strip()
        self.assertEqual(self.added_at, added_at)

    def test_shows_add_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_button = soup.find(id="add-button").get_text().strip()
        self.assertIn("Add", add_button)
