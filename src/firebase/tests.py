"""Houses tests for the firebase app."""

import json
from unittest.mock import ANY, MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile


class VerifyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("verify")

    @patch("firebase.views.authenticate")
    @patch("firebase.views.login")
    def test_auth_success(self, mock_login: MagicMock, mock_authenticate: MagicMock):
        mock_user = MagicMock()
        mock_authenticate.return_value = mock_user
        response = self.client.post(
            self.url,
            data=json.dumps({"idToken": "fake"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["valid"])
        mock_authenticate.assert_called_once_with(ANY, id_token="fake")  # noqa: S106 (Hard-coded for testing.)
        mock_login.assert_called_once_with(
            ANY, mock_user, backend="firebase.backends.FirebaseBackend"
        )

    @patch("firebase.views.authenticate")
    def test_auth_failure(self, mock_authenticate: MagicMock):
        mock_authenticate.return_value = None
        response = self.client.post(
            self.url,
            data=json.dumps({"idToken": "fake"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["valid"])

    def test_invalid_json(self):
        response = self.client.post(
            self.url, data="invalid", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["valid"])


class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("signup")
        self.user = User.objects.create(username="aketchum", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

    def test_already_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email")
        self.assertContains(response, "Password")
        self.assertContains(response, "Submit")
        self.assertContains(response, "Google")
        self.assertContains(response, "Microsoft")


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create(username="aketchum", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

    def test_already_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email")
        self.assertContains(response, "Password")
        self.assertContains(response, "Submit")
        self.assertContains(response, "Google")
        self.assertContains(response, "Microsoft")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("logout")
        self.user = User.objects.create(username="aketchum", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

    def test_already_logged_out(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_logout(self):
        self.client.force_login(self.user)
        self.assertIn("_auth_user_id", self.client.session)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ViewProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("view-profile")
        self.user = User.objects.create(username="aketchum", password="pikachu")  # noqa: S106 (Hard-coded for testing.)
        self.user_profile = UserProfile.objects.create(user=self.user)

    @patch("firebase.views.read_user_profile")
    def test_no_user_profile(self, mock_read_user_profile: MagicMock):
        mock_read_user_profile.return_value = None
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    @patch("firebase.views.read_user_profile")
    def test_has_user_profile(self, mock_read_user_profile: MagicMock):
        mock_read_user_profile.return_value = self.user_profile, self.user
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("view-profile")
        self.user = User.objects.create(username="aketchum", password="pikachu")  # noqa: S106 (Hard-coded for testing.)
        self.user_profile = UserProfile.objects.create(user=self.user)

    @patch("firebase.views.read_user_profile")
    def test_no_user_profile(self, mock_read_user_profile: MagicMock):
        mock_read_user_profile.return_value = None
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    @patch("firebase.views.read_user_profile")
    def test_has_user_profile(self, mock_read_user_profile: MagicMock):
        mock_read_user_profile.return_value = self.user_profile, self.user
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
