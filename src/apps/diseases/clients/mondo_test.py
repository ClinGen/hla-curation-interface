"""Test the Mondo client.

This module contains tests for the `MondoClient` class, which is responsible
for fetching and processing disease data from the Mondo Disease Ontology API.
"""

from unittest.mock import Mock

import pytest

from apps.diseases.clients.mondo import MondoClient, MondoClientError
from base.clients import EntityClientError, HTTPClient
from constants import MondoConstants


@pytest.fixture
def json_data_valid() -> dict:
    """Return valid JSON data from the Mondo API.

    This is the expected format of the JSON data returned by the Mondo API.
    """
    return {"label": "disease label", "other": "info"}


@pytest.fixture
def json_data_invalid() -> dict:
    """Return invalid JSON data from the Mondo API.

    This response is missing the fields we care about.
    """
    return {"other": "info"}


@pytest.fixture
def expected() -> dict:
    """Return the data we expect to extract from the JSON data."""
    return {"label": "disease label"}


@pytest.fixture
def mondo_id() -> str:
    """Return a Mondo ID to be used in tests."""
    return "MONDO_0000001"


@pytest.fixture
def mock_response_valid_data(json_data_valid: dict) -> Mock:
    """Return a mocked response from the Mondo API with valid data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = json_data_valid
    return mock_response


@pytest.fixture
def mock_response_invalid_data(json_data_invalid: dict) -> Mock:
    """Return a mocked response from the Mondo API with invalid data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = json_data_invalid
    return mock_response


@pytest.fixture
def mock_client_valid_data(
    mock_response_valid_data: Mock, mondo_id: str
) -> MondoClient:
    """Return a `MondoClient` whose response has valid data."""
    mock_http_client = Mock(spec=HTTPClient)
    mock_http_client.get.return_value = mock_response_valid_data
    client = MondoClient(mondo_id=mondo_id)
    client._http_client = mock_http_client  # noqa: SLF001 (We want to access the private member to inject the mock client.)
    return client


@pytest.fixture
def mock_client_invalid_data(
    mock_response_invalid_data: Mock, mondo_id: str
) -> MondoClient:
    """Return a `MondoClient` whose response has invalid data."""
    mock_http_client = Mock(spec=HTTPClient)
    mock_http_client.get.return_value = mock_response_invalid_data
    client = MondoClient(mondo_id=mondo_id)
    client._http_client = mock_http_client  # noqa: SLF001 (We want to access the private member to inject the mock client.)
    return client


@pytest.fixture
def mock_client_http_error(mondo_id: str) -> MondoClient:
    """Return a `MondoClient` that raises an HTTP error."""
    mock_http_client = Mock(spec=HTTPClient)
    mock_http_client.get.side_effect = EntityClientError("HTTP Error")
    client = MondoClient(mondo_id=mondo_id)
    client._http_client = mock_http_client  # noqa: SLF001 (We want to access the private member to inject the mock client.)
    return client


class TestMondoClient:
    """Make sure `MondoClient` works as expected.

    This class tests initialization, data fetching, and data population.
    """

    @pytest.mark.unit
    def test_initialization(self, mondo_id: str) -> None:
        """Test proper initialization of `MondoClient`."""
        client = MondoClient(mondo_id=mondo_id)
        assert client.base_url == MondoConstants.API_URL
        assert client.mondo_id == mondo_id
        assert client.label is None

    @pytest.mark.unit
    def test_fetch_success(self, mock_client_valid_data: Mock, expected: dict) -> None:
        """Test successful API data fetching."""
        client = mock_client_valid_data
        client.fetch()
        assert client.label == expected["label"]

    @pytest.mark.unit
    def test_fetch_failure_invalid_data(
        self, mondo_id: str, mock_client_invalid_data: MondoClient
    ) -> None:
        """Test handling of data extraction failures."""
        client = mock_client_invalid_data
        with pytest.raises(MondoClientError) as exc:
            client.fetch()
        error_message = f"Error validating data for {mondo_id}"
        assert error_message in str(exc.value)
        assert client.label is None

    @pytest.mark.unit
    def test_fetch_failure_request(
        self, mock_client_http_error: MondoClient, mondo_id: str
    ) -> None:
        """Test handling of HTTP request failures."""
        client = mock_client_http_error
        with pytest.raises(MondoClientError) as exc:
            client.fetch()
        error_message = f"Error fetching Mondo data for {mondo_id}"
        assert error_message in str(exc.value)
        assert client.label is None
