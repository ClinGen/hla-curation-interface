"""Provide selectors for HLA alleles."""

from django.db.models import Q, QuerySet

from apps.markers.models.allele import Allele
from base.selectors import EntitySelector


class AlleleSelector(EntitySelector):
    """Get a specific HLA allele or get a list of HLA alleles."""

    def get(self, car_id: str) -> Allele | None:
        """Return a specific HLA allele.

        Args:
             car_id: The ClinGen Allele Registry ID of the allele.

        Returns:
            The HLA allele object or `None` if the CAR ID is not found.
        """
        return Allele.objects.filter(car_id=car_id).first()

    def list(self, query: str | None = None) -> QuerySet[Allele] | None:
        """Return a list of all HLA alleles, optionally filtered.

        Args:
             query: The string to filter the HLA alleles by.

        Returns:
            The HLA alleles matching the query.
        """
        if query is None:
            return Allele.objects.all()
        return Allele.objects.filter(
            Q(descriptor__icontains=query) | Q(car_id__icontains=query)
        )
