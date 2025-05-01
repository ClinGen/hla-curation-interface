"""Provide base classes for services."""

from abc import ABC, abstractmethod
from typing import Any


class EntityService(ABC):
    """Create or update an entity.

    Here an entity refers to a model in the HCI that has a new page, an all page,
    and an overview page. Some examples include: curations, diseases, markers (alleles
    and haplotypes), and publications.
    """

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Create an entity."""

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Update an entity."""
