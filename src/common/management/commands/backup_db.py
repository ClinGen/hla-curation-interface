"""Backs up the database under daily/, for the nightly systemd timer."""

import socket
import traceback

from django.core.management import call_command
from django.core.management.base import BaseCommand

from common.alerts import send_alert


class Command(BaseCommand):
    help = "Back up the database under daily/, and email an alert if it fails."

    def handle(self, *_args: object, **_options: object) -> None:
        """Back up the database, and email ALERT_EMAILS if the backup fails.

        The error is raised again after the alert, so systemd marks the run failed.
        send_alert never raises, so a broken mail setup can't hide the error.
        """
        try:
            call_command("dbbackup", "--noinput", "--compress")
        except Exception:
            send_alert(
                "Nightly database backup failed",
                f"The nightly database backup on {socket.gethostname()} failed:\n\n"
                f"{traceback.format_exc()}",
            )
            raise
