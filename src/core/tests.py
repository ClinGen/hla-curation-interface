"""Houses tests for the core app."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("home")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "HLA Curation Interface")


class AboutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("about")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "About")
        self.assertContains(response, "HLA Curation Interface (HCI)")
        self.assertContains(response, "alleles")
        self.assertContains(response, "haplotypes")
        self.assertContains(response, "Stanford University")


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("contact")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Contact")
        self.assertContains(response, "email")
        self.assertContains(response, "hci@clinicalgenome.org")


class HelpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("help")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Help")
        self.assertContains(response, "standard operating procedure")
        self.assertContains(response, "email")
        self.assertContains(response, "hci@clinicalgenome.org")


class CitingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("citing")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Citing")
        self.assertContains(response, "format")
        self.assertContains(response, "dataset")


class AcknowledgementsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("acknowledgements")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Acknowledgements")
        self.assertContains(response, "NIH/NHGRI")
        self.assertContains(response, "Steven Mack")


class CollaboratorsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("collaborators")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Collaborators")
        self.assertContains(response, "The Baylor College of Medicine ClinGen Team")
        self.assertContains(response, "ClinPGx")


class AccountActivationMessageTest(TestCase):
    def setUp(self):
        self.user1_no_phi_no_perms = User.objects.create(
            username="user1",
            password="user1pw",  # noqa: S106 (Hard-coded for testing.)
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1_no_phi_no_perms,
            has_signed_phi_agreement=False,
            has_curation_permissions=False,
        )
        self.user2_yes_phi_no_perms = User.objects.create(
            username="user2",
            password="user2pw",  # noqa: S106 (Hard-coded for testing.)
        )
        self.user2_profile = UserProfile.objects.create(
            user=self.user2_yes_phi_no_perms,
            has_signed_phi_agreement=True,
            has_curation_permissions=False,
        )
        self.user3_no_phi_yes_perms = User.objects.create(
            username="user3",
            password="user3pw",  # noqa: S106 (Hard-coded for testing.)
        )
        self.user3_profile = UserProfile.objects.create(
            user=self.user3_no_phi_yes_perms,
            has_signed_phi_agreement=False,
            has_curation_permissions=True,
        )
        self.user4_yes_phi_yes_perms = User.objects.create(
            username="user4",
            password="user4pw",  # noqa: S106 (Hard-coded for testing.)
        )
        self.user4_profile = UserProfile.objects.create(
            user=self.user4_is_active_is_verified,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
        )
        self.client = Client()
        self.url = reverse("home")
        self.NO_PHI_MSG = "You haven't signed the PHI agreement yet."
        self.NO_PERMS_MSG = "Your user account does not have curation permissions."

    def test_message_for_no_phi_no_perms(self):
        self.client.force_login(self.user1_no_phi_no_perms)
        response = self.client.get(self.url)
        self.assertContains(response, self.NO_PERMS_MSG)
        self.assertContains(response, self.NO_PERMS_MSG)

    def test_message_for_yes_phi_no_perms(self):
        self.client.force_login(self.user2_yes_phi_no_perms)
        response = self.client.get(self.url)
        self.assertNotContains(response, self.NO_PHI_MSG)
        self.assertContains(response, self.NO_PERMS_MSG)

    def test_message_for_no_phi_yes_perms(self):
        self.client.force_login(self.user3_no_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, self.NO_PHI_MSG)
        self.assertNotContains(response, self.NO_PERMS_MSG)

    def test_message_for_yes_phi_yes_perms(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertNotContains(response, self.NO_PHI_MSG)
        self.assertNotContains(response, self.NO_PERMS_MSG)
