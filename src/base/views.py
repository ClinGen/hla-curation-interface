"""Provide base classes for views."""

from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse


class EntityView(ABC):
    """Create, view all, or view a specific entity.

    Here an entity refers to a model in the HCI that has a new page, a list page,
    and a details page. Some examples include: curations, diseases, markers (alleles
    and haplotypes), and publications.

    We ignore the type hints and docstring docs for the `*args` and `**kwargs`
    parameters because we don't know what they will be or whether the child class will
    use them. They are there to provide flexibility to the child class.
    """

    @staticmethod
    @abstractmethod
    def new(request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003, D417
        """Return the page that provides a form that creates a new entity.

        Args:
             request: The Django HTTP request object.
        """

    @staticmethod
    @abstractmethod
    def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003, D417
        """Return the searchable table page for an entity.

        Args:
             request: The Django HTTP request object.
        """

    @staticmethod
    @abstractmethod
    def details(request: HttpRequest, *args, **kwargs) -> HttpResponse:  # noqa: ANN002, ANN003, D417
        """Return the details page for an entity.

        Args:
            request: The Django HTTP request object.
        """
