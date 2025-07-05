"""Houses code that interacts with third-party services for the allele app."""

import logging

import requests

MONDO_URL = "https://www.ebi.ac.uk/ols4/api/ontologies/mondo/terms?iri=http://purl.obolibrary.org/obo"

logger = logging.getLogger(__name__)


def fetch_disease_data(mondo_id: str, timeout: int = 5) -> dict | None:
    """Fetches Mondo disease data from the Ontology Lookup Service.

    Args:
        mondo_id: The Mondo Disease Ontology ID for the disease.
        timeout: The timeout for the HTTP request in seconds.

    Returns:
        The API endpoint's JSON or None if there was an error.
    """
    try:
        mondo_id = mondo_id.replace(":", "_")
        response = requests.get(f"{MONDO_URL}/{mondo_id}", timeout=timeout)
        response.raise_for_status()
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        Exception,
    ):
        message = "Unable to get disease data from OLS"
        logger.exception(message)
        return None
    else:
        return response.json()


def get_name(data: dict) -> str:
    """Extracts the disease name from the OLS response.

    Args:
        data: The data fetched from the OLS.

    Returns:
        The disease name in the data if present or an empty string otherwise.
    """
    name = ""
    if (
        "_embedded" in data
        and "terms" in data["_embedded"]
        and len(data["_embedded"]["terms"]) > 0
        and "label" in data["_embedded"]["terms"][0]
    ):
        name = data["_embedded"]["terms"][0]["label"]
    if name == "":
        logger.warning("Unable to get name from OLS data; returning empty string")
    return name


def get_iri(data: dict) -> str:
    """Extracts the internationalized resource identifier from the OLS response.

    Args:
        data: The data fetched from the OLS.

    Returns:
        The IRI in the data if present or an empty string otherwise.
    """
    iri = ""
    if (
        "_embedded" in data
        and "terms" in data["_embedded"]
        and len(data["_embedded"]["terms"]) > 0
        and "iri" in data["_embedded"]["terms"][0]
    ):
        iri = data["_embedded"]["terms"][0]["iri"]
    if iri == "":
        logger.warning("Unable to get IRI from OLS data; returning empty string")
    return iri
