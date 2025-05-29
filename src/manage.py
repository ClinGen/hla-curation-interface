#!/usr/bin/env python
"""Provides a command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Runs administrative tasks.

    Raises:
        ImportError: When Django can't be imported.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        error_message = "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you forget to activate "
        "a virtual environment?"
        raise ImportError(error_message) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
