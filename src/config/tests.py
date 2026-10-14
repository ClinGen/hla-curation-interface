"""Houses tests for the project's settings."""

import importlib
import os
from types import ModuleType
from unittest.mock import patch

from django.test import SimpleTestCase


def import_base_settings(environ: dict[str, str]) -> ModuleType:
    """Import a fresh copy of the base settings module with extra environment variables.

    Args:
        environ: Environment variables to set while importing.

    Returns:
        The base settings module.
    """
    with patch("sentry_sdk.init"), patch.dict(os.environ, environ):
        base = importlib.import_module("config.settings.base")
        return importlib.reload(base)


def import_prod_settings() -> ModuleType:
    """Import a fresh copy of the production settings module.

    Returns:
        The production settings module.
    """
    # Keep the import from initializing Sentry with the real DSN from .env.
    with patch("sentry_sdk.init"):
        prod = importlib.import_module("config.settings.prod")
        return importlib.reload(prod)


class ProdLoggingTest(SimpleTestCase):
    """Checks that production logs go only to stderr, which journald collects."""

    def setUp(self):
        self.prod = import_prod_settings()

    def test_no_file_handlers(self):
        handler_classes = [h["class"] for h in self.prod.LOGGING["handlers"].values()]
        self.assertFalse([c for c in handler_classes if c.endswith("FileHandler")])

    def test_root_logs_to_console_only(self):
        self.assertEqual(self.prod.LOGGING["root"]["handlers"], ["console"])

    def test_console_format_includes_logger_name(self):
        formatter = self.prod.LOGGING["handlers"]["console"]["formatter"]
        self.assertIn("{name}", self.prod.LOGGING["formatters"][formatter]["format"])

    def test_log_file_settings_are_gone(self):
        self.assertFalse(hasattr(self.prod, "LOG_DIR"))
        self.assertFalse(hasattr(self.prod, "LOG_FILE"))


class AlertEmailsSettingTest(SimpleTestCase):
    def test_parses_comma_separated_addresses_with_spaces(self):
        base = import_base_settings({"ALERT_EMAILS": " a@example.com, b@example.com ,"})
        self.assertEqual(base.ALERT_EMAILS, ["a@example.com", "b@example.com"])

    def test_is_empty_when_unset(self):
        base = import_base_settings({"ALERT_EMAILS": ""})
        self.assertEqual(base.ALERT_EMAILS, [])
