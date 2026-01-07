"""Houses code that interacts with third-party services for the publication app."""

import logging
import os

import requests
from bs4 import BeautifulSoup, PageElement
from lxml import etree

from publication.models import PublicationTypes

BIORXIV_URL = "https://api.biorxiv.org/details/biorxiv/"
MEDRXIV_URL = "https://api.biorxiv.org/details/medrxiv/"
PUBMED_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key={os.getenv('PUBMED_API_KEY')}&db=PubMed&retmode=xml&id="

logger = logging.getLogger(__name__)


def fetch_pubmed_data(pubmed_id: str, timeout: int = 5) -> BeautifulSoup | None:
    """Fetches data about a PubMed article.

    Args:
        pubmed_id: The PubMed ID for the article.
        timeout: The timeout for the HTTP request in seconds.

    Returns:
        The API endpoint's XML or None if there was an error.
    """
    try:
        response = requests.get(f"{PUBMED_URL}/{pubmed_id}", timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "xml")
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        etree.XMLSyntaxError,
        Exception,
    ):
        message = "Unable to get data from PubMed"
        logger.exception(message)
        return None
    else:
        return soup


def get_pubmed_title(soup: BeautifulSoup) -> str:
    """Extracts the title from the PubMed response.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        The title of the article if it can be found or an empty string otherwise.
    """
    title = soup.find("ArticleTitle") or ""
    if isinstance(title, PageElement):
        return title.get_text(strip=True)
    logger.warning("Unable to get title from PubMed data; returning empty string")
    return title


def get_pubmed_author(soup: BeautifulSoup) -> str:
    """Extracts the author from the PubMed response.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        The first author in the author list if it can be found or an empty string
        otherwise.
    """
    author = soup.find("LastName") or ""  # Find the first instance of LastName.
    if isinstance(author, PageElement):
        return author.get_text(strip=True)
    logger.warning("Unable to get author from PubMed data; returning empty string")
    return author


def get_pubmed_year(soup: BeautifulSoup) -> int | None:
    """Extracts the publication year from the PubMed response.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        The year of publication if it can be found as an integer, or None otherwise.
    """
    year = soup.find("Year")
    if isinstance(year, PageElement):
        year_text = year.get_text(strip=True)
        try:
            return int(year_text)
        except (ValueError, TypeError):
            logger.warning(
                f"Unable to convert year '{year_text}' to integer; returning None"
            )
            return None
    logger.warning("Unable to get year from PubMed data; returning None")
    return None


def fetch_rxiv_data(rxiv_type: str, doi: str, timeout: int = 5) -> dict | None:
    """Fetches data about bioRxiv or medRxiv paper.

    Args:
        rxiv_type: The type code for either bioRxiv or medRxiv publications.
        doi: The digital object identifier for the paper.
        timeout: The timeout for the HTTP request in seconds.

    Returns:
        The API endpoint's JSON or None if there was an error.
    """
    url = BIORXIV_URL if rxiv_type == PublicationTypes.BIORXIV else MEDRXIV_URL
    try:
        response = requests.get(f"{url}/{doi}", timeout=timeout)
        response.raise_for_status()
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.Timeout,
        requests.exceptions.TooManyRedirects,
        etree.XMLSyntaxError,
        Exception,
    ):
        message = "Unable to get data from PubMed"
        logger.exception(message)
        return None
    else:
        return response.json()


def get_rxiv_title(data: dict) -> str:
    """Extracts the title from the Rxiv response.

    Args:
        data: The data fetched from Rxiv.

    Returns:
        The title if it can be found or an empty string otherwise.
    """
    title = ""
    if "collection" in data:
        collection_length = len(data["collection"])
        if (
            collection_length > 0
            and "title" in data["collection"][collection_length - 1]
        ):
            # Get the most recent title.
            title = data["collection"][collection_length - 1]["title"]
    return title


def get_rxiv_author(data: dict) -> str:
    """Extracts the author from the Rxiv response.

    Args:
        data: The data fetched from Rxiv.

    Returns:
        The first author in the authors list if it can be found or an empty string
        otherwise.
    """
    author = ""
    if "collection" in data:
        collection_length = len(data["collection"])
        if (
            collection_length > 0
            and "authors" in data["collection"][collection_length - 1]
        ):
            # Get the most recent title.
            authors_list = data["collection"][collection_length - 1]["authors"]
            author = authors_list.split(";")[0]
    return author


def get_rxiv_year(data: dict) -> int | None:
    """Extracts the publication year from the Rxiv response.

    Args:
        data: The data fetched from Rxiv.

    Returns:
        The publication year if it can be found or None otherwise.
    """
    if "collection" in data:
        collection_length = len(data["collection"])
        if (
            collection_length > 0
            and "date" in data["collection"][collection_length - 1]
        ):
            try:
                # The format is typically yyyy-mm-dd.
                date_str = data["collection"][collection_length - 1]["date"]
                year_str = date_str.split("-")[0]
                return int(year_str)
            except (ValueError, TypeError, IndexError):
                logger.warning("Unable to extract year from date; returning None")
    logger.warning("Unable to get year from Rxiv data; returning None")
    return None
