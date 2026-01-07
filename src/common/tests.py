"""Houses code used commonly in tests."""

from django.contrib.auth.models import User
from django.test import Client

from core.models import UserProfile


class ViewTestMixin:
    def test_get_successful(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)

    def test_page_name_in_response(self):
        response = self.client.get(self.url)
        self.assertContains(response, self.page_name)

    def test_expected_text_in_response(self):
        response = self.client.get(self.url)
        for text in self.expected_text:
            self.assertContains(response, text)


class CreateTestMixin:
    def setUp(self):
        super().setUp()
        self.client = Client()
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

    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_permission_denied_if_no_phi_no_perms(self):
        self.client.force_login(self.user1_no_phi_no_perms)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_yes_phi_no_perms(self):
        self.client.force_login(self.user2_yes_phi_no_perms)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_no_phi_yes_perms(self):
        self.client.force_login(self.user3_no_phi_yes_perms)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_granted_if_yes_phi_yes_perms(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
