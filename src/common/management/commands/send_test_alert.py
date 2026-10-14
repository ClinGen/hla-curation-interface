"""Sends a test alert to ALERT_EMAILS, to check that email works."""

from django.core.management.base import BaseCommand, CommandError

from common.alerts import send_alert


class Command(BaseCommand):
    help = "Send a test alert to ALERT_EMAILS, to check that email works."

    def handle(self, *_args: object, **_options: object) -> None:
        """Send the test alert.

        Raises:
            CommandError: If the alert wasn't sent. The log says why.
        """
        if not send_alert("Test alert", "If you got this, alert emails work."):
            msg = "The test alert wasn't sent. See the log for why."
            raise CommandError(msg)
        self.stdout.write("Sent a test alert.")
