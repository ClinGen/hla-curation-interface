"""Houses code used commonly in tests."""

import logging
import os
import re
import sqlite3
from contextlib import closing, contextmanager
from io import StringIO
from pathlib import Path
from smtplib import SMTPException
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from dbbackup import settings as dbbackup_settings
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail
from django.core.management import CommandError, call_command
from django.db import connection
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from auth_.models import UserProfile
from common.alerts import send_alert
from common.tables import HistoryTable
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
        for name in (
            "taskforce_evidence_summary",
            "taskforce_additional_notes",
            "taskforce_review_date",
        ):
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
        tables = sorted(Path(settings.BASE_DIR).glob("*/tables.py"))
        for path in self._templates() + tables:
            for match in pattern.finditer(path.read_text()):
                with self.subTest(path=path.name, classes=match.group(0)):
                    self.assertIn("is-link", match.group(0))

    def test_no_primary_color(self):
        for path in self._templates():
            with self.subTest(path=path.name):
                self.assertNotIn("is-primary", path.read_text())

    def _taskforce_review(self, status: str) -> str:
        curation = SimpleNamespace(status=status, taskforce_display="HLA Taskforce")
        return render_to_string(
            "curation/partials/taskforce_review.html", {"curation": curation}
        )

    def test_sent_back_feedback_is_red(self):
        self.assertIn('class="message is-danger', self._taskforce_review("INP"))

    def test_other_feedback_is_neutral(self):
        html = self._taskforce_review("APR")
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


class HistoryTableHideUserTest(TestCase):
    def test_shows_changed_by_by_default(self):
        table = HistoryTable([], change_url_name="allele-change")
        self.assertIn("history_user", table.columns.names())

    def test_hide_user_drops_changed_by(self):
        table = HistoryTable([], change_url_name="allele-change", hide_user=True)
        self.assertNotIn("history_user", table.columns.names())


class TempBackupStorageMixin:
    """Sends backups to a temporary directory, available as self.backup_dir.

    django-dbbackup reads STORAGES["dbbackup"] once, at import, so this patches its
    settings module instead of using override_settings.
    """

    addCleanup: Any

    def use_temp_backup_storage(self):
        """Patch django-dbbackup's storage to a new temporary directory."""
        backup_dir = TemporaryDirectory()
        self.addCleanup(backup_dir.cleanup)
        self.backup_dir = Path(backup_dir.name)
        for patcher in (
            patch.object(
                dbbackup_settings,
                "STORAGE",
                "django.core.files.storage.FileSystemStorage",
            ),
            patch.object(
                dbbackup_settings,
                "STORAGE_OPTIONS",
                {"location": str(self.backup_dir)},
            ),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)


class DatabaseBackupTest(TempBackupStorageMixin, TransactionTestCase):
    """Tests that django-dbbackup can back up and restore our SQLite database.

    The test database is in memory, but restoring copies the backup over the file
    named by the database's NAME, so the restore test points NAME at a temporary file
    and reads that file.
    """

    backup_name = "pre-deployment/x.sqlite3.gz"

    def setUp(self):
        self.use_temp_backup_storage()

    def back_up(self):
        """Back up the test database to the temporary backup directory."""
        call_command(
            "dbbackup",
            "--noinput",
            "--compress",
            "-o",
            self.backup_name,
            stdout=StringIO(),
        )

    def test_backup_writes_file(self):
        self.back_up()
        self.assertTrue((self.backup_dir / self.backup_name).is_file())

    def test_restore_brings_back_row_deleted_after_backup(self):
        User.objects.create(username="kept")
        self.back_up()
        User.objects.filter(username="kept").delete()
        restored_db = self.backup_dir / "restored.sqlite3"
        # dbrestore closes the connection first. With NAME pointing at a file, Django
        # would really close the in-memory test database, which deletes it for every
        # later test, so keep the connection open.
        with (
            patch.dict(connection.settings_dict, {"NAME": str(restored_db)}),
            patch.object(connection, "close"),
        ):
            call_command(
                "dbrestore",
                "--noinput",
                "--uncompress",
                "-i",
                self.backup_name,
                stdout=StringIO(),
            )
        with closing(sqlite3.connect(restored_db)) as restored:
            usernames = restored.execute("SELECT username FROM auth_user").fetchall()
        self.assertIn(("kept",), usernames)


class AdminBackupViewTest(
    TempBackupStorageMixin, SuppressRequestLoggingMixin, TransactionTestCase
):
    """Tests the admin's Back up now button.

    This is a TransactionTestCase because SQLite's backup API waits forever on the
    transaction a TestCase holds open.
    """

    url = reverse("admin-backup")

    def setUp(self):
        self.use_temp_backup_storage()
        self.superuser = User.objects.create_superuser(username="admin@example.com")
        self.staff = User.objects.create_user(
            username="staff@example.com", is_staff=True
        )

    def manual_backups(self) -> list[Path]:
        """Return the backups, not their metadata files, under manual/."""
        return sorted((self.backup_dir / "manual").glob("*.gz"))

    def test_superuser_post_backs_up_and_names_the_backup(self):
        self.client.force_login(self.superuser)
        response = self.client.post(self.url, follow=True)
        backups = self.manual_backups()
        self.assertEqual(len(backups), 1)
        self.assertIn("admin-example.com", backups[0].name)
        self.assertRedirects(response, reverse("admin:index"))
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(any(f"manual/{backups[0].name}" in m for m in messages))

    def test_staff_who_isnt_superuser_is_forbidden(self):
        self.client.force_login(self.staff)
        with self.suppress_request_logging():
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.manual_backups(), [])

    def test_anonymous_post_redirects_to_admin_login(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={self.url}",
            target_status_code=200,
        )
        self.assertEqual(self.manual_backups(), [])

    def test_get_is_not_allowed(self):
        self.client.force_login(self.superuser)
        with self.suppress_request_logging():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.manual_backups(), [])

    def test_failed_backup_shows_an_error_instead_of_a_500(self):
        self.client.force_login(self.superuser)
        with (
            patch("common.views.call_command", side_effect=CommandError("boom")),
            self.assertLogs("common.views", level="ERROR"),
        ):
            response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, reverse("admin:index"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual([m.level_tag for m in messages], ["error"])

    def test_admin_index_shows_button_to_superusers_only(self):
        self.client.force_login(self.superuser)
        self.assertContains(self.client.get(reverse("admin:index")), self.url)
        self.client.force_login(self.staff)
        self.assertNotContains(self.client.get(reverse("admin:index")), self.url)


class ListBackupsCommandTest(TempBackupStorageMixin, TestCase):
    """Tests list_backups, which finds backups stored under prefixes like daily/."""

    def setUp(self):
        self.use_temp_backup_storage()

    def add_backup(self, name: str, modified: int) -> None:
        """Write a fake backup file with the given modification time.

        Args:
            name: The backup's name, relative to the backup storage.
            modified: The file's modification time, in seconds since the epoch.
        """
        path = self.backup_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"backup")
        os.utime(path, (modified, modified))

    def list_backups(self) -> list[str]:
        """Run list_backups.

        Returns:
            The lines it printed.
        """
        out = StringIO()
        call_command("list_backups", stdout=out)
        return out.getvalue().splitlines()

    def test_lists_backups_under_prefixes_oldest_first(self):
        self.add_backup("pre-deployment/hci-test-a-to-b.sqlite3.gz", 2_000_000_000)
        self.add_backup("daily/hci-test-2026-10-14.sqlite3.gz", 1_900_000_000)
        lines = self.list_backups()
        self.assertEqual(
            [line.split()[-1] for line in lines],
            [
                "daily/hci-test-2026-10-14.sqlite3.gz",
                "pre-deployment/hci-test-a-to-b.sqlite3.gz",
            ],
        )

    def test_skips_metadata_files(self):
        self.add_backup("daily/hci-test.sqlite3.gz", 1_900_000_000)
        self.add_backup("daily/hci-test.sqlite3.gz.metadata", 1_900_000_000)
        self.assertEqual(len(self.list_backups()), 1)

    def test_says_so_when_there_are_none(self):
        self.assertEqual(self.list_backups(), ["No backups found."])


@override_settings(
    SUBDOMAIN="hci-test", ALERT_EMAILS=["a@example.com", "b@example.com"]
)
class SendAlertTest(TestCase):
    """Tests the helper that emails ALERT_EMAILS when something goes wrong."""

    def test_sends_one_message_to_every_alert_address(self):
        self.assertTrue(send_alert("Backup failed", "Details"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["a@example.com", "b@example.com"])
        self.assertIn("hci-test", mail.outbox[0].subject)
        self.assertIn("Backup failed", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].body, "Details")

    @override_settings(ALERT_EMAILS=[])
    def test_sends_nothing_without_alert_addresses(self):
        with self.assertLogs("common.alerts", level="WARNING"):
            self.assertFalse(send_alert("Backup failed", "Details"))
        self.assertEqual(mail.outbox, [])

    def test_logs_instead_of_raising_when_sending_fails(self):
        with (
            patch("common.alerts.send_mail", side_effect=SMTPException("down")),
            self.assertLogs("common.alerts", level="ERROR"),
        ):
            self.assertFalse(send_alert("Backup failed", "Details"))

    def test_send_test_alert_command_sends_an_alert(self):
        call_command("send_test_alert", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ALERT_EMAILS=[])
    def test_send_test_alert_command_fails_when_nothing_is_sent(self):
        with (
            self.assertLogs("common.alerts", level="WARNING"),
            self.assertRaises(CommandError),
        ):
            call_command("send_test_alert", stdout=StringIO())


class BackupDbCommandTest(TempBackupStorageMixin, TransactionTestCase):
    """Tests the nightly backup command that the systemd timer runs.

    This is a TransactionTestCase because SQLite's backup API waits forever on the
    transaction a TestCase holds open.
    """

    def setUp(self):
        self.use_temp_backup_storage()

    def test_writes_one_backup_under_daily(self):
        call_command("backup_db", stdout=StringIO())
        self.assertEqual(len(list((self.backup_dir / "daily").glob("*.gz"))), 1)

    def test_failure_sends_an_alert_and_propagates(self):
        with (
            patch(
                "common.management.commands.backup_db.call_command",
                side_effect=CommandError("disk full"),
            ),
            patch("common.management.commands.backup_db.send_alert") as send_alert,
            patch(
                "common.management.commands.backup_db.socket.gethostname",
                return_value="hci-lightsail-test",
            ),
            self.assertRaisesMessage(CommandError, "disk full"),
        ):
            call_command("backup_db", stdout=StringIO())
        send_alert.assert_called_once()
        subject, body = send_alert.call_args.args
        self.assertIn("backup failed", subject.lower())
        self.assertIn("hci-lightsail-test", body)
        self.assertIn("disk full", body)
