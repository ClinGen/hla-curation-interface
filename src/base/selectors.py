"""Provide base classes for selectors."""

from abc import ABC, abstractmethod
from typing import Any


class EntitySelector(ABC):
    """Get a specific entity or get a list of entities from the database.

    Here an entity refers to a model in the HCI that has a new page, an all page,
    and an overview page. Some examples include: curations, diseases, markers (alleles
    and haplotypes), and publications.
    """

    @abstractmethod
    def get(self, human_readable_id: str) -> Any:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Return a specific entity based on its human-readable ID.

        Args:
             human_readable_id: The human-readable ID of the model for the entity.

        Returns:
            The entity.
        """

    @abstractmethod
    def list(self, query: str | None) -> Any:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Return all entities or a subset of entities based on the query.

        Args:
            query: The string to filter the entities by.

        Returns:
            The entities matching the query.
        """
