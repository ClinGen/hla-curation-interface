"""Houses tests for the firebase app."""

import json
from unittest.mock import ANY, MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from firebase.clients import get_token_info
from firebase.crud import create_firebase_user, read_firebase_user, update_firebase_user


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
        self.user = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

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
        self.user = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

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
        self.user = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)

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
        self.user = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)
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
        self.user = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)
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


class FirebaseClientTest(TestCase):
    def setUp(self):
        self.uid = "abc123"
        self.email = "foo@bar.org"
        self.email_verified = True
        self.picture = "https://www.bar.org/image.jpg"
        self.name = "Foo Bar"
        self.sign_in_provider = "password"
        self.decoded_token_no_uid_or_email = {
            "uid": None,
            "email": None,
        }
        self.decoded_token_valid = {
            "uid": self.uid,
            "email": self.email,
            "email_verified": self.email_verified,
            "picture": self.picture,
            "name": self.name,
            "firebase": {"sign_in_provider": self.sign_in_provider},
        }

    def test_invalid_token(self):
        with self.assertLogs("firebase.clients", level="ERROR"):
            get_token_info("")

    @patch("firebase.clients.auth.verify_id_token")
    def test_no_uid_or_email_token(self, mock_verify_id_token: MagicMock):
        mock_verify_id_token.return_value = self.decoded_token_no_uid_or_email
        info = get_token_info("garbage")
        self.assertIsNone(info)

    @patch("firebase.clients.auth.verify_id_token")
    def test_valid_token(self, mock_verify_id_token: MagicMock):
        mock_verify_id_token.return_value = self.decoded_token_valid
        info = get_token_info("garbage")
        self.assertEqual(self.uid, info["username"])
        self.assertEqual(self.email, info["email"])
        self.assertEqual(self.email_verified, info["email_verified"])
        self.assertEqual(self.picture, info["photo_url"])
        self.assertEqual(self.name, info["display_name"])
        self.assertEqual(self.sign_in_provider, info["provider"])


class CRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="ash",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            email="ash@kantomail.net",
        )

    def test_create_with_non_existent_user(self):
        create_firebase_user("misty", "misty@pokemail.com")
        self.assertTrue(User.objects.filter(username="misty").exists())

    def test_create_with_existing_user(self):
        user = create_firebase_user(self.user.username, self.user.email)
        self.assertTrue(User.objects.filter(username=self.user.username).exists())
        self.assertEqual(self.user.username, user.username)

    def test_read_with_non_existent_user(self):
        user = read_firebase_user("brock")
        self.assertIsNone(user)

    def test_read_with_existing_user(self):
        user = read_firebase_user("ash")
        self.assertTrue(User.objects.filter(username=self.user.username).exists())
        self.assertEqual(self.user.username, user.username)

    def test_update_non_existent_user(self):
        user = update_firebase_user("oak", "oak@kanto.edu")
        self.assertIsNone(user)

    def test_update_existing_user(self):
        new_email = "aketchum@kantomail.net"
        user = update_firebase_user("ash", new_email)
        self.assertEqual(new_email, user.email)
