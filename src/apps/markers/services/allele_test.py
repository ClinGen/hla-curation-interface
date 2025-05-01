"""Test allele services."""

from unittest.mock import Mock

import pytest

from apps.markers.services.allele import AlleleService
from constants import CARConstants


@pytest.fixture
def mock_allele_client() -> Mock:
    """Return a mocked HLA allele client."""
    client = Mock()
    client.descriptor = "A*01:01:01:119"
    client.car_id = "CAHLA123"
    client.car_url = f"{CARConstants.API_URL}/{client.descriptor}"
    client.schema = Mock()
    return client


@pytest.mark.component
@pytest.mark.django_db
def test_create_allele(mock_allele_client: Mock) -> None:
    """Make sure we can create an allele."""
    descriptor = "A*01:01:01:119"
    client = mock_allele_client
    service = AlleleService(client)
    allele = service.create(descriptor)
    assert allele is not None
    assert allele.car_id == client.car_id
    assert allele.car_url == client.car_url
