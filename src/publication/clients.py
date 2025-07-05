"""Houses code that interacts with third-party services for the publication app."""

import logging
import os

import requests
from bs4 import BeautifulSoup, PageElement
from lxml import etree

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
