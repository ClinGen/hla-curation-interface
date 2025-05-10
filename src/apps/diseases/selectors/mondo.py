"""Provide selectors for Mondo diseases."""

from django.db.models import Q, QuerySet

from apps.diseases.models.mondo import Mondo
from base.selectors import EntitySelector


class MondoSelector(EntitySelector):
    """Get a specific Mondo disease or get a list of Mondo diseases."""

    def get(self, mondo_id: str) -> Mondo | None:
        """Return a specific Mondo disease.

        Args:
             mondo_id: The Mondo ID of the disease.

        Returns:
            The Mondo disease object or `None` if the Mondo ID is not found.
        """
        return Mondo.objects.filter(mondo_id=mondo_id).first()

    def list(self, query: str | None = None) -> QuerySet[Mondo] | None:
        """Return a list of all Mondo diseases, optionally filtered.

        Args:
             query: The string to filter the Mondo diseases by.

        Returns:
            The Mondo diseases matching the query.
        """
        if query is None:
            return Mondo.objects.all()
        return Mondo.objects.filter(
            Q(mondo_id__icontains=query) | Q(label__icontains=query)
        )
