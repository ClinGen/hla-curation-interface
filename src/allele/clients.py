"""Houses code that interacts with third-party services for the allele app."""

import logging

import requests

CAR_URL = "https://reg.genome.network/allele/hla/desc"

logger = logging.getLogger(__name__)


def fetch_allele_data(name: str, timeout: int = 5) -> list[dict] | None:
    """Fetches allele data from the ClinGen Allele Registry.

    Args:
        name: The name of the allele.
        timeout: The timeout for the HTTP request in seconds.

    Returns:
        The API endpoint's JSON or None if there was an error.
    """
    try:
        response = requests.get(f"{CAR_URL}/{name}", timeout=timeout)
        response.raise_for_status()
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        Exception,
    ):
        message = "Unable to get allele data from CAR"
        logger.exception(message)
        return None
    else:
        return response.json()


def get_car_id(data: list[dict] | None) -> str | None:
    """Extracts the ClinGen Allele Registry ID from the CAR response.

    Args:
        data: The data fetched from the CAR.

    Returns:
        The CAR ID in the data if present or None otherwise.
    """
    car_id = None
    if data is not None and len(data) > 0 and "id" in data[0]:
        car_id = data[0]["id"]
    if car_id is None:
        logger.warning("Unable to get name from OLS data; returning None")
    return car_id
