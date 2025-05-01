"""Provide base classes for clients."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any
from xml.etree import ElementTree as ET

import requests

from constants import RequestsConstants

logger = logging.getLogger(__name__)


class EntityClientError(Exception):
    """Raise when a client encounters an error."""


class EntityClientRequestError(Exception):
    """Raise when a client encounters a request error."""


class EntityClientJSONError(Exception):
    """Raise when a client can't decode JSON."""


class EntityClientXMLError(Exception):
    """Raise when a client can't parse XML."""


class HTTPClient(ABC):
    """Perform HTTP requests to an external source."""

    @abstractmethod
    def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | None = None,
    ) -> Any:  # noqa: ANN401 (We don't care about this for abstract methods.)
        """Perform a GET request to the external source."""


class RequestsHTTPClient(HTTPClient):
    """Perform HTTP requests to an external source using the `requests` library."""

    def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: float | None = None,
    ) -> requests.Response:
        """Perform a GET request to the external source using the `requests` library.

        Returns:
             The response from the external source.
        """
        return requests.get(url, params=params, headers=headers, timeout=timeout)


class EntityClient:
    """Get data from an external source."""

    def __init__(
        self,
        base_url: str = "",
        timeout: int = RequestsConstants.DEFAULT_TIMEOUT,
        http_client: HTTPClient | None = None,
    ) -> None:
        """Set the base URL and timeout.

        Args:
             base_url: The base URL of the external source, e.g., "https://example.com".
             timeout: The timeout in seconds for the request.
             http_client: The HTTP client to use for the request.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.headers: dict = {}
        self._http_client = http_client or RequestsHTTPClient()

    def _get(self, endpoint: str, params: dict | None = None) -> requests.Response:
        """Perform a GET request to the external source.

        Args:
            endpoint: The portion of the URL after the base, e.g., "path/to/resource".
            params: Query parameters to be included in the request.

        Raises:
            EntityClientRequestError: If the request fails.

        Returns:
             The response from the external source.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"GET {url} params {params}")
            logger.debug(f"    Params: {params}")
            logger.debug(f"    Headers: {self.headers}")
            response = self._http_client.get(
                url, params=params, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            error_message = f"Error during GET request to {url}: {exc}"
            raise EntityClientRequestError(error_message) from exc
        return response

    def get_json(self, endpoint: str, params: dict | None = None) -> dict:
        """Perform a GET request to the external source and return the JSON response.

        Args:
            endpoint: The portion of the URL after the base, e.g., "path/to/resource".
            params: Query parameters to be included in the request.

        Raises:
             EntityClientJSONError: If the JSON can't be decoded.

        Returns:
            A dictionary representing the JSON response.
        """
        response = self._get(endpoint, params=params)
        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            error_message = f"Failed to decode JSON from response: {exc}"
            raise EntityClientJSONError(error_message) from exc
        return data

    def get_xml(self, endpoint: str, params: dict | None = None) -> ET.Element:
        """Perform a GET request to the external source and return the XML response.

        Args:
            endpoint: The portion of the URL after the base, e.g., "path/to/resource".
            params: Query parameters to be included in the request.

        Raises:
            EntityClientXMLError: If the XML can't be parsed.

        Returns:
            An `Element` object representing the XML response.
        """
        response = self._get(endpoint, params=params)
        try:
            data = ET.fromstring(response.content)
        except ET.ParseError as exc:
            error_message = f"Failed to parse XML from response: {exc}"
            raise EntityClientXMLError(error_message) from exc
        return data

    @abstractmethod
    def fetch(self) -> None:
        """Fetch data from the external source and populate the members.

        This method provides an explicit method to call to perform the HTTP request.
        It should be overridden by subclasses.
        """
