"""Houses code used commonly in tests."""

import logging
import re
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.test import Client, TestCase
from django.urls import reverse

from auth_.models import UserProfile
from common.templatetags.custom_filters import is_public


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
            password="user1pw",  # ruff: ignore[hardcoded-password-func-arg] (Hard-coded for testing.)
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1_no_phi_no_perms,
            has_signed_phi_agreement=False,
            has_curation_permissions=False,
        )
        self.user2_yes_phi_no_perms = User.objects.create(
            username="user2",
            password="user2pw",  # ruff: ignore[hardcoded-password-func-arg] (Hard-coded for testing.)
        )
        self.user2_profile = UserProfile.objects.create(
            user=self.user2_yes_phi_no_perms,
            has_signed_phi_agreement=True,
            has_curation_permissions=False,
        )
        self.user3_no_phi_yes_perms = User.objects.create(
            username="user3",
            password="user3pw",  # ruff: ignore[hardcoded-password-func-arg] (Hard-coded for testing.)
        )
        self.user3_profile = UserProfile.objects.create(
            user=self.user3_no_phi_yes_perms,
            has_signed_phi_agreement=False,
            has_curation_permissions=True,
        )
        self.user4_yes_phi_yes_perms = User.objects.create(
            username="user4",
            password="user4pw",  # ruff: ignore[hardcoded-password-func-arg] (Hard-coded for testing.)
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


def field_block(html: str, field_id: str) -> str:
    """Returns the rendered HTML from a field's label up to its control.

    The public badge sits between the two, so tests use this to check whether a
    given field has one.
    """
    start = html.index(f'for="{field_id}"') if f'for="{field_id}"' in html else None
    if start is None:
        start = html.index(f'data-field="{field_id}"')
    return html[start : html.index('class="control"', start)]


class IsPublicFilterTest(TestCase):
    def test_public_curation_fields(self):
        for name in ("ep_evidence_summary", "ep_additional_notes", "ep_review_date"):
            with self.subTest(name=name):
                self.assertTrue(is_public(name, "curation"))

    def test_internal_curation_fields(self):
        for name in ("decision", "status"):
            with self.subTest(name=name):
                self.assertFalse(is_public(name, "curation"))

    def test_evidence_form_fields_map_to_model_fields(self):
        self.assertTrue(is_public("p_value_string", "evidence"))
        self.assertTrue(is_public("cohort_size", "evidence"))

    def test_internal_evidence_fields(self):
        for name in ("p_value_notes", "needs_review", "needs_review_notes"):
            with self.subTest(name=name):
                self.assertFalse(is_public(name, "evidence"))


class PublicBadgeTooltipTest(TestCase):
    """The globe badge shows its meaning in a Tippy tooltip, never beside it."""

    TOOLTIP = "This will be visible in the public-facing HLArepo once published."

    def test_badge_has_tooltip_and_no_title(self):
        html = render_to_string("common/public_badge.html")
        self.assertIn(f'data-tippy-content="{self.TOOLTIP}"', html)
        self.assertIn("bi-globe2", html)
        self.assertNotIn("title=", html)

    def test_badge_is_keyboard_focusable(self):
        html = render_to_string("common/public_badge.html")
        self.assertIn('tabindex="0"', html)

    def test_section_heading_badge(self):
        html = render_to_string(
            "common/form/section_heading.html",
            {"id": "p-value", "text": "p-value", "public": True},
        )
        self.assertIn('<h2 id="p-value" class="title is-4">', html)
        self.assertIn("public-badge", html)

    def test_section_heading_without_badge(self):
        html = render_to_string(
            "common/form/section_heading.html", {"id": "x", "text": "X"}
        )
        self.assertNotIn("public-badge", html)

    def test_base_layout_loads_tippy(self):
        html = self.client.get(reverse("home")).content.decode()
        for asset in (
            "hci/css/tippy.css",
            "hci/js/popper.min.js",
            "hci/js/tippy.umd.min.js",
            "hci/js/tooltips.js",
        ):
            with self.subTest(asset=asset):
                self.assertIn(static(asset), html)


class ColorKeyTest(TestCase):
    """Checks templates against the color key in docs/design.md."""

    TAG_COLORS = {
        "in_progress": "",
        "not_provided": "",
        "provisional": "is-warning",
        "needs_review": "is-danger",
        "done": "is-success",
        "provided": "is-success",
        "approved": "is-success",
        "published": "is-info",
    }
    COLOR_MODIFIERS = {"is-warning", "is-danger", "is-success", "is-info"}

    @staticmethod
    def _tag_classes(name: str) -> set[str]:
        html = render_to_string(f"common/tags/{name}.html")
        match = re.search(r'class="([^"]*)"', html)
        assert match is not None
        return set(match.group(1).split())

    @staticmethod
    def _templates() -> list[Path]:
        return sorted(Path(settings.BASE_DIR).glob("**/templates/**/*.html"))

    def test_status_tag_colors(self):
        for name, color in self.TAG_COLORS.items():
            with self.subTest(name=name):
                classes = self._tag_classes(name)
                self.assertEqual(classes & self.COLOR_MODIFIERS, {color} - {""})
                self.assertIn("is-light", classes)

    def test_every_tag_template_is_in_the_key(self):
        tags_dir = Path(settings.BASE_DIR) / "common/templates/common/tags"
        names = {p.stem for p in tags_dir.glob("*.html")} - {"_generic"}
        self.assertEqual(names, set(self.TAG_COLORS))

    def test_buttons_are_link_blue(self):
        pattern = re.compile(r'class="button\b[^"]*"')
        for path in self._templates():
            for match in pattern.finditer(path.read_text()):
                with self.subTest(path=path.name, classes=match.group(0)):
                    self.assertIn("is-link", match.group(0))

    def test_no_primary_color(self):
        for path in self._templates():
            with self.subTest(path=path.name):
                self.assertNotIn("is-primary", path.read_text())

    def _ep_review(self, status: str) -> str:
        curation = SimpleNamespace(status=status, ep_display="HLA EP")
        return render_to_string(
            "curation/partials/ep_review.html", {"curation": curation}
        )

    def test_sent_back_feedback_is_red(self):
        self.assertIn('class="message is-danger', self._ep_review("INP"))

    def test_other_feedback_is_neutral(self):
        html = self._ep_review("APR")
        self.assertIn('class="message mt-2"', html)


class MigrationsUpToDateTest(TestCase):
    """Fails when a model change has no migration."""

    def test_no_missing_migrations(self):
        try:
            call_command("makemigrations", "--check", "--dry-run", stdout=StringIO())
        except SystemExit:
            self.fail("Model changes are missing a migration. Run makemigrations.")


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
