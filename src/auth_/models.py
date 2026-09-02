"""Houses database models for the core app."""

from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords


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
    has_review_permissions = models.BooleanField(
        default=False,
        verbose_name="EP Review Permissions",
        help_text="Whether the user can act as an EP reviewer.",
    )
    clerk_user_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Clerk User ID",
        help_text="The Clerk user ID for this account; populated on first Clerk login.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When the user profile was last updated.",
    )
    history = HistoricalRecords()

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
        """Whether the user is allowed to create stuff in the HCI."""
        return (
            self.user.is_authenticated
            and self.has_curation_permissions
            and self.has_signed_phi_agreement
        )

    @property
    def can_review(self) -> bool:
        """Whether the user can act as an EP reviewer."""
        return self.has_review_permissions and self.can_curate
