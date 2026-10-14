"""Emails alerts, such as a failed nightly backup, to ALERT_EMAILS."""

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_alert(subject: str, body: str) -> bool:
    """Email an alert to ALERT_EMAILS.

    This never raises. A broken mail setup is logged instead, so it can't hide the
    error that the alert is about.

    Args:
        subject: The subject line, without the subdomain prefix.
        body: The message.

    Returns:
        Whether the alert was sent.
    """
    if not settings.ALERT_EMAILS:
        logger.warning(f"ALERT_EMAILS is empty, so this alert wasn't sent: {subject}")
        return False
    try:
        send_mail(
            f"[{settings.SUBDOMAIN}] {subject}",
            body,
            None,
            settings.ALERT_EMAILS,
        )
    except (SMTPException, OSError):
        logger.exception(f"Couldn't send this alert: {subject}")
        return False
    return True
