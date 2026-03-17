from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from auth_.models import UserProfile
from common.tests import OpenViewTestMixin


class HomeViewTest(OpenViewTestMixin, TestCase):
    url = reverse("home")
    template = "core/home.html"
    page_name = "Home"
    expected_text = ["HLA Curation Interface"]


class AboutViewTest(OpenViewTestMixin, TestCase):
    url = reverse("about")
    template = "core/about.html"
    page_name = "About"
    expected_text = [
        "HLA Curation Interface (HCI)",
        "alleles",
        "haplotypes",
        "Stanford University",
    ]


class ContactViewTest(OpenViewTestMixin, TestCase):
    url = reverse("contact")
    template = "core/contact.html"
    page_name = "Contact"
    expected_text = ["email", "hci@clinicalgenome.org"]


class HelpViewTest(OpenViewTestMixin, TestCase):
    url = reverse("help")
    template = "core/help.html"
    page_name = "Help"
    expected_text = ["standard operating procedure", "email", "hci@clinicalgenome.org"]


class CitingViewTest(OpenViewTestMixin, TestCase):
    url = reverse("citing")
    template = "core/citing.html"
    page_name = "Citing"
    expected_text = ["format", "dataset"]


class AcknowledgementsViewTest(OpenViewTestMixin, TestCase):
    url = reverse("acknowledgements")
    template = "core/acknowledgements.html"
    page_name = "Acknowledgements"
    expected_text = ["NIH/NHGRI", "Steven Mack"]


class CollaboratorsViewTest(OpenViewTestMixin, TestCase):
    url = reverse("collaborators")
    template = "core/collaborators.html"
    page_name = "Collaborators"
    expected_text = [
        "The Baylor College of Medicine ClinGen Team",
        "ClinPGx",
    ]


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
            user=self.user4_yes_phi_yes_perms,
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
