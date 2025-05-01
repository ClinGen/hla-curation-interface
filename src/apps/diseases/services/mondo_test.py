"""Test Mondo services."""

import pytest

from apps.diseases.models.mondo import Mondo
from apps.diseases.services.mondo import MondoService, MondoServiceError


class MockDiseaseClient:
    """Mock the disease client."""

    def __init__(self, mondo_id: str) -> None:
        """Initialize the mock client."""
        self.mondo_id = mondo_id
        self.label = "disease label"


@pytest.mark.component
@pytest.mark.django_db
def test_create_mondo_disease() -> None:
    """Make sure we can create a Mondo disease."""
    mondo_id = "MONDO_1234"
    client = MockDiseaseClient(mondo_id)
    service = MondoService(client)  # type: ignore (We are using a mock client for our test.)
    disease = service.create(mondo_id)
    assert disease is not None
    assert disease.mondo_id == client.mondo_id
    assert disease.label == client.label


@pytest.mark.component
@pytest.mark.django_db
def test_update_mondo_disease() -> None:
    """Make sure we can update a Mondo disease."""
    mondo_id = "MONDO_5432"
    Mondo.objects.create(mondo_id=mondo_id, label="disease label")
    client = MockDiseaseClient(mondo_id)
    service = MondoService(client)  # type: ignore (We are using a mock client for our test.)
    service.update(mondo_id, "new disease label")
    disease = Mondo.objects.get(mondo_id=mondo_id)
    assert disease is not None
    assert disease.mondo_id == client.mondo_id
    assert disease.label == "new disease label"


@pytest.mark.component
@pytest.mark.django_db
def test_update_non_existent_mondo_disease() -> None:
    """Make sure we can't update a non-existent Mondo disease."""
    mondo_id = "MONDO_6789"
    client = MockDiseaseClient(mondo_id)
    service = MondoService(client)  # type: ignore (We are using a mock client for our test.)
    with pytest.raises(MondoServiceError):
        service.update(mondo_id, "new disease label")
