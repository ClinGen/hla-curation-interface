"""Provides test settings."""

import sentry_sdk

from .dev import *  # ruff: ignore[undefined-local-with-import-star]

# Disable Sentry during tests to prevent background HTTP flushes to the ingest endpoint,
# which pollute test output with urllib3/asyncio DEBUG logs when root is at DEBUG level.
sentry_sdk.init()

# Replace dev.py's console StreamHandler with a null handler so logs don't print to
# stderr during test runs. pytest installs its own LogCaptureHandler on root alongside
# this and shows captured logs only for failing tests. assertLogs() is unaffected: it
# adds a capturing handler directly on the named logger, independent of root config.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
    "loggers": {
        # Suppress asyncio DEBUG logs that fire during Clerk SDK's process-exit
        # finalizer; without this the finalizer triggers a log write after
        # pytest-xdist has already closed its capture stream, printing
        # "--- Logging error ---" to the terminal after every worker exits.
        "asyncio": {"level": "WARNING"},
    },
}
