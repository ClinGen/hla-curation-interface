"""Houses tests for the firebase app."""

import json
from unittest.mock import ANY, MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse


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
        mock_authenticate.assert_called_once_with(ANY, id_token="fake")  # noqa: S106 (It's a fake token for testing.)
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
