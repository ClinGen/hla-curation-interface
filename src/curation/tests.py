"""Houses tests for the curation app."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from core.models import UserProfile
from curation.models import Curation


class CurationCreateTest(TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("curation-create")
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

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        breadcrumb = soup.find("nav", {"class": "breadcrumb"})
        self.assertIsNotNone(breadcrumb)

    def test_shows_radio_buttons(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_radio_button = soup.find(id="id_curation_type_0")
        self.assertIsNotNone(allele_radio_button)
        haplotype_radio_button = soup.find(id="id_curation_type_1")
        self.assertIsNotNone(haplotype_radio_button)

    def test_shows_allele_select(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_select = soup.find(id="id_allele")
        self.assertIsNotNone(allele_select)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"})
        self.assertIsNotNone(submit_button)

    def test_creates_allele_curation_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "ALL", "allele": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        self.assertIsNotNone(new_curation)
        self.assertEqual(new_curation.curation_type, "ALL")  # type: ignore[union-attr]
        self.assertEqual(new_curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.added_by, self.user_who_can_create)  # type: ignore[union-attr]

    def test_creates_haplotype_curation_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "HAP", "haplotype": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        self.assertIsNotNone(new_curation)
        self.assertEqual(new_curation.curation_type, "ALL")  # type: ignore[union-attr]
        self.assertEqual(new_curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.added_by, self.user_who_can_create)  # type: ignore[union-attr]
