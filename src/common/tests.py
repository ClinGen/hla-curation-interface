"""Houses code used commonly in tests."""

import logging
from contextlib import contextmanager
from typing import Any

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from auth_.models import UserProfile


class SuppressRequestLoggingMixin:
    """Mixin that provides a context manager to silence expected django.request logs."""

    @contextmanager
    def suppress_request_logging(self):
        """Temporarily suppress django.request logging to hide expected 403s."""
        logger = logging.getLogger("django.request")
        previous_level = logger.level
        logger.setLevel(logging.CRITICAL)
        try:
            yield
        finally:
            logger.setLevel(previous_level)


class BaseViewTestMixin:
    """Base mixin with common view tests."""

    url: str
    template: str
    page_name: str
    expected_text: list[str]
    # The following are provided by TestCase in concrete test classes.
    client: Any
    setUp: Any
    assertEqual: Any
    assertContains: Any
    assertTemplateUsed: Any

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


class OpenViewTestMixin(BaseViewTestMixin):
    """Mixin for views that are open to the public.

    Adds test that anonymous users get 200 status code.
    """

    def test_get_successful(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class ProtectedViewTestMixin(SuppressRequestLoggingMixin, BaseViewTestMixin):
    """Mixin for views that require authentication and curation permissions.

    Sets up 4 test users with different permission combinations and tests
    that only users with both PHI agreement and curation permissions can
    access the view.
    """

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
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_permission_denied_if_no_phi_no_perms(self):
        self.client.force_login(self.user1_no_phi_no_perms)
        with self.suppress_request_logging():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_yes_phi_no_perms(self):
        self.client.force_login(self.user2_yes_phi_no_perms)
        with self.suppress_request_logging():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_no_phi_yes_perms(self):
        self.client.force_login(self.user3_no_phi_yes_perms)
        with self.suppress_request_logging():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_granted_if_yes_phi_yes_perms(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class SearchListViewTest(ProtectedViewTestMixin, TestCase):
    """Tests for the two behaviors SearchListView adds beyond a plain ListView.

    Uses the allele list view as a representative endpoint since it has a
    simple fixture and short search_fields list. ProtectedViewTestMixin is
    included so setUp() creates the four permission-combination users; each
    test logs in as user4 (PHI + curation permissions) to satisfy the view's
    ProtectedViewMixin before exercising SearchListView behavior.
    """

    fixtures = ["test_alleles.json"]
    url = reverse("allele-list")
    template = "allele/list.html"
    page_name = "Allele Search"
    expected_text = []

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_full_page_returned_without_hx_request_header(self):
        response = self.client.get(self.url)
        # Full page: list.html is the top-level template (it includes the partial).
        self.assertTemplateUsed(response, "allele/list.html")

    def test_partial_returned_with_hx_request_header(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST="true")
        # HTMX response: only the partial is rendered, not the full page.
        self.assertTemplateUsed(response, "common/partials/search_results.html")
        self.assertTemplateNotUsed(response, "allele/list.html")

    def test_search_returns_matching_rows(self):
        response = self.client.get(self.url, {"q": "A*01:02:03"})
        self.assertContains(response, "A000001")
        self.assertContains(response, "1 result")
        self.assertNotContains(response, "A000002")

    def test_search_with_no_match_returns_zero_results(self):
        response = self.client.get(self.url, {"q": "zzz_no_match"})
        self.assertContains(response, "0 results")
        self.assertNotContains(response, "A000001")

    def test_empty_query_returns_all_rows(self):
        response_no_q = self.client.get(self.url)
        response_empty_q = self.client.get(self.url, {"q": ""})
        self.assertEqual(
            response_no_q.context["result_count"],
            response_empty_q.context["result_count"],
        )
        self.assertContains(response_empty_q, "A000001")
        self.assertContains(response_empty_q, "A000002")
        self.assertContains(response_empty_q, "A000003")
