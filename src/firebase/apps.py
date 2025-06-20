"""Provides the configuration for the firebase app."""

import os
from pathlib import Path

import firebase_admin
from django.apps import AppConfig
from firebase_admin import credentials

from config.settings.base import BASE_DIR


class FirebaseConfig(AppConfig):
    """Configures the firebase app."""

    name = "firebase"

    def ready(self) -> None:
        """Sets up the Firebase Admin SDK."""
        if os.getenv("CI") or os.getenv("READTHEDOCS"):
            return
        service_account_key_path = Path(BASE_DIR / "firebase-account-key.json")
        if not firebase_admin._apps:  # noqa: SLF001 (Avoid initializing multiple times in development.)
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred)
