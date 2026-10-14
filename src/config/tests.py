"""Houses tests for the project's settings."""

import importlib
from types import ModuleType
from unittest.mock import patch

from django.test import SimpleTestCase


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
