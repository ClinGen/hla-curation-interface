"""Defines database models for the repo app."""

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class PublishedCuration(models.Model):
    """References a curation that has been published to the repository."""

    curation = models.OneToOneField(
        "curation.Curation",
        on_delete=models.PROTECT,
        related_name="publication",
        unique=True,
        help_text="The curation that has been published.",
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Published At",
        help_text="When the curation was published.",
    )
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="curations_published",
        help_text="The user who published the curation.",
    )
    version = models.IntegerField(
        default=1,
        help_text="Version number for this publication.",
    )

    class Meta:
        """Provides Django model metadata for PublishedCuration."""

        db_table = "published_curation"
        verbose_name = "Published Curation"
        verbose_name_plural = "Published Curations"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        """Returns a string representation of the published curation."""
        return f"Published: {self.curation.slug}"

    def get_absolute_url(self) -> str:
        """Returns the URL for the published curation detail page."""
        return reverse("repo-detail", kwargs={"curation_slug": self.curation.slug})
