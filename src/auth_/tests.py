"""Houses tests for the auth_ app."""

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import View

from auth_.backends import ClerkBackend
from auth_.models import UserProfile
from auth_.permissions import ReviewerViewMixin


class CanReviewPropertyTest(TestCase):
    @staticmethod
    def _make_user(*, phi: bool, curate: bool, review: bool) -> User:
        user = User.objects.create_user(
            username=f"u_{phi}_{curate}_{review}",
            password="pw",  # ruff: ignore[hardcoded-password-func-arg]
        )
        UserProfile.objects.create(
            user=user,
            has_signed_phi_agreement=phi,
            has_curation_permissions=curate,
            has_review_permissions=review,
        )
        return user

    def test_can_review_requires_all_three_flags(self):
        user = self._make_user(phi=True, curate=True, review=True)
        profile = user.profile  # type: ignore
        self.assertTrue(profile.can_review)

    def test_can_review_false_without_review_flag(self):
        user = self._make_user(phi=True, curate=True, review=False)
        profile = user.profile  # type: ignore
        self.assertFalse(profile.can_review)

    def test_can_review_false_without_curate_flag(self):
        user = self._make_user(phi=True, curate=False, review=True)
        profile = user.profile  # type: ignore
        self.assertFalse(profile.can_review)

    def test_can_review_false_without_phi(self):
        user = self._make_user(phi=False, curate=True, review=True)
        profile = user.profile  # type: ignore
        self.assertFalse(profile.can_review)

    def test_can_review_false_when_all_flags_false(self):
        user = self._make_user(phi=False, curate=False, review=False)
        profile = user.profile  # type: ignore
        self.assertFalse(profile.can_review)


class ReviewerViewMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.reviewer = User.objects.create_user(username="reviewer", password="pw")  # ruff: ignore[hardcoded-password-func-arg]
        UserProfile.objects.create(
            user=self.reviewer,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
            has_review_permissions=True,
        )

        self.curator = User.objects.create_user(username="curator", password="pw")  # ruff: ignore[hardcoded-password-func-arg]
        UserProfile.objects.create(
            user=self.curator,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
            has_review_permissions=False,
        )

        class _DummyView(ReviewerViewMixin, View):
            @staticmethod
            def get(
                _request: object, *_args: object, **_kwargs: object
            ) -> HttpResponse:
                return HttpResponse("ok")

        self.view = _DummyView.as_view()

    def test_reviewer_can_access(self):
        request = self.factory.get("/")
        request.user = self.reviewer
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

    def test_non_reviewer_gets_403(self):
        request = self.factory.get("/")
        request.user = self.curator
        with self.assertRaises(PermissionDenied):
            self.view(request)


class ClerkBackendTest(TestCase):
    def test_returns_none_without_clerk_user_id(self):
        backend = ClerkBackend()
        result = backend.authenticate(None, clerk_email="test@example.com")
        self.assertIsNone(result)

    def test_new_user_created_when_no_match(self):
        backend = ClerkBackend()
        user = backend.authenticate(
            None, clerk_user_id="user_new", clerk_email="new@example.com"
        )
        self.assertIsNotNone(user)
        assert user is not None
        self.assertEqual(user.username, "new@example.com")
        self.assertEqual(user.profile.clerk_user_id, "user_new")  # type: ignore

    def test_existing_user_matched_by_clerk_id(self):
        existing = User.objects.create_user(username="existing@example.com")
        profile, _ = UserProfile.objects.get_or_create(user=existing)
        profile.clerk_user_id = "user_existing"
        profile.save()

        backend = ClerkBackend()
        user = backend.authenticate(
            None, clerk_user_id="user_existing", clerk_email="existing@example.com"
        )
        assert user is not None
        self.assertEqual(user.pk, existing.pk)
        self.assertEqual(
            User.objects.filter(username="existing@example.com").count(), 1
        )

    def test_workos_migration_matches_by_email_and_writes_clerk_id(self):
        old_user = User.objects.create_user(username="migrated@example.com")
        profile = UserProfile.objects.create(
            user=old_user,
            has_curation_permissions=True,
            has_signed_phi_agreement=True,
        )

        backend = ClerkBackend()
        user = backend.authenticate(
            None, clerk_user_id="user_clerk_123", clerk_email="migrated@example.com"
        )
        assert user is not None
        self.assertEqual(user.pk, old_user.pk)
        profile.refresh_from_db()
        self.assertEqual(profile.clerk_user_id, "user_clerk_123")
        # Existing permission flags must not be overwritten.
        self.assertTrue(profile.has_curation_permissions)
        self.assertTrue(profile.has_signed_phi_agreement)


def _make_clerk_user(_clerk_user_id: str, email: str) -> MagicMock:
    """Returns a mock Clerk user object with one primary email address."""
    email_obj = MagicMock()
    email_obj.id = "iea_primary"
    email_obj.email_address = email
    mock_user = MagicMock()
    mock_user.primary_email_address_id = "iea_primary"
    mock_user.email_addresses = [email_obj]
    return mock_user


class CallbackViewTest(TestCase):
    CALLBACK_URL = "/auth/callback"

    @patch("auth_.views.verify_token")
    @patch("auth_.views.clerk")
    def test_success_establishes_session(
        self, mock_clerk: MagicMock, mock_verify: MagicMock
    ):
        mock_verify.return_value = {"sub": "user_abc", "sid": "sess_xyz"}
        mock_clerk.users.get.return_value = _make_clerk_user(
            "user_abc", "hello@example.com"
        )
        self.client.cookies["__session"] = "valid_token"
        response = self.client.get(self.CALLBACK_URL)
        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
        self.assertIn("_auth_user_id", self.client.session)

    def test_missing_cookie_redirects_to_login(self):
        response = self.client.get(self.CALLBACK_URL)
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)

    @patch("auth_.views.verify_token")
    def test_invalid_token_redirects_to_login(self, mock_verify: MagicMock):
        mock_verify.side_effect = Exception("bad token")
        self.client.cookies["__session"] = "garbage"
        with self.assertLogs("auth_.views", level="ERROR"):
            response = self.client.get(self.CALLBACK_URL)
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)

    @patch("auth_.views.verify_token")
    @patch("auth_.views.clerk")
    def test_no_primary_email_redirects_to_login(
        self, mock_clerk: MagicMock, mock_verify: MagicMock
    ):
        mock_verify.return_value = {"sub": "user_noemail", "sid": "sess_1"}
        no_email_user = MagicMock()
        no_email_user.primary_email_address_id = "iea_missing"
        no_email_user.email_addresses = []
        mock_clerk.users.get.return_value = no_email_user
        self.client.cookies["__session"] = "valid_token"
        with self.assertLogs("auth_.views", level="WARNING"):
            response = self.client.get(self.CALLBACK_URL)
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
