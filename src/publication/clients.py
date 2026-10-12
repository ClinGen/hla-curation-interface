"""Houses code that interacts with third-party services for the publication app."""

import logging
import os

import requests
from bs4 import BeautifulSoup, PageElement, Tag
from lxml import etree

PUBMED_URL = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key={os.getenv('PUBMED_API_KEY')}&db=PubMed&retmode=xml"

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
        response = requests.get(f"{PUBMED_URL}&id={pubmed_id}", timeout=timeout)
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


def _get_author_elements(soup: BeautifulSoup) -> list[Tag]:
    """Returns the article's Author elements in order, or [] if there are none."""
    author_list = soup.select_one("MedlineCitation > Article > AuthorList")
    if author_list is None:
        return []
    return author_list.find_all("Author", recursive=False)


def _get_text(author: Tag, name: str) -> str:
    element = author.find(name, recursive=False)
    return element.get_text(strip=True) if element else ""


def get_pubmed_author(soup: BeautifulSoup) -> str:
    """Extracts the primary author's surname from the PubMed response.

    Group authors are skipped, since they have no surname.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        The surname of the first person in the author list if it can be found or an
        empty string otherwise.
    """
    for author in _get_author_elements(soup):
        last_name = _get_text(author, "LastName")
        if last_name:
            return last_name
    logger.warning("Unable to get author from PubMed data; returning empty string")
    return ""


def get_pubmed_authors(soup: BeautifulSoup) -> list[str]:
    """Extracts every author from the PubMed response, in order.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        Each author as "LastName Initials", or the group name for group authors, or
        an empty list if there's no author list.
    """
    names = []
    for author in _get_author_elements(soup):
        collective_name = _get_text(author, "CollectiveName")
        last_name = _get_text(author, "LastName")
        initials = _get_text(author, "Initials")
        name = collective_name or f"{last_name} {initials}".strip()
        if name:
            names.append(name)
    if not names:
        logger.warning("Unable to get authors from PubMed data; returning []")
    return names


def get_pubmed_year(soup: BeautifulSoup) -> int | None:
    """Extracts the publication year from the PubMed response.

    Args:
        soup: The BeautifulSoup object representing the PubMed response.

    Returns:
        The year of publication if it can be found as an integer, or None otherwise.
    """
    pub_date = soup.find("PubDate")
    if pub_date:
        year = pub_date.find("Year")
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
