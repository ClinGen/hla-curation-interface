"""Provide base classes for views."""

from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse


class EntityView(ABC):
    """Create, view all, or view a specific entity.

    Here an entity refers to a model in the HCI that has a new page, an all page,
    and an overview page. Some examples include: curations, diseases, markers (alleles
    and haplotypes), and publications.
    """

    @abstractmethod
    def new(self, request: HttpRequest) -> HttpResponse:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Return the page that provides a form that creates a new entity.

        Args:
             request: The Django HTTP request object.
        """

    @abstractmethod
    def list(self, request: HttpRequest) -> HttpResponse:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Return the searchable table page for an entity.

        Args:
             request: The Django HTTP request object.
        """

    @abstractmethod
    def details(self, request: HttpRequest, human_readable_id: str) -> HttpResponse:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Return the details page for an entity.

        Args:
            request: The Django HTTP request object.
            human_readable_id: The human-readable ID of the model for the entity.
        """
