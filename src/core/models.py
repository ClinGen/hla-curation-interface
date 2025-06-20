"""Houses database models for the core app."""

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Extends the built-in Django User model with additional information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    firebase_uid = models.CharField(
        blank=True,
        max_length=128,
        null=True,
        unique=True,
        verbose_name="Firebase User ID",
        help_text="The user ID from Firebase.",
    )
    firebase_email_verified = models.BooleanField(
        default=False,
        verbose_name="Firebase Email Verified",
        help_text="Whether the email address has been verified by Firebase.",
    )
    firebase_photo_url = models.URLField(
        blank=True,
        default="",
        max_length=500,
        verbose_name="Firebase Photo URL",
        help_text="The URL of the user's profile picture from Firebase.",
    )
    firebase_display_name = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name="Firebase Display Name",
        help_text="The user's display name from Firebase.",
    )
    firebase_sign_in_provider = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name="Firebase Sign-In Provider",
        help_text="The provider used to sign the user in.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "core_user_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        """Returns a string representation of the UserProfile object."""
        return f"{self.user.email}/{self.user.username}"
