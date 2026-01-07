"""Houses database models for the core app."""

from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """Extends the built-in Django User model with additional information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    has_curation_permissions = models.BooleanField(
        default=False,
        verbose_name="Curation Permissions",
        help_text="Whether the user should be able to curate.",
    )
    has_signed_phi_agreement = models.BooleanField(
        default=False,
        verbose_name="PHI Agreement",
        help_text="Whether the user has signed the PHI agreement.",
    )

    class Meta:
        """Provides metadata."""

        db_table = "core_user_profile"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        """Returns a string representation of the UserProfile object."""
        return self.user.email

    @property
    def can_curate(self) -> bool:
        """Returns whether the user is allowed to create stuff in the HCI."""
        return (
            self.user.is_authenticated
            and self.has_curation_permissions
            and self.has_signed_phi_agreement
        )
