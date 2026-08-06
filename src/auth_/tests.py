"""Houses tests for the auth_ app."""

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.views.generic import View

from auth_.models import UserProfile
from auth_.permissions import ReviewerViewMixin


class CanReviewPropertyTest(TestCase):
    @staticmethod
    def _make_user(*, phi: bool, curate: bool, review: bool) -> User:
        user = User.objects.create_user(
            username=f"u_{phi}_{curate}_{review}",
            password="pw",  # noqa: S106
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

        self.reviewer = User.objects.create_user(username="reviewer", password="pw")  # noqa: S106
        UserProfile.objects.create(
            user=self.reviewer,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
            has_review_permissions=True,
        )

        self.curator = User.objects.create_user(username="curator", password="pw")  # noqa: S106
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
