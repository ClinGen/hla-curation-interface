# type: ignore
"""Provide services related to PubMed."""
# TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
# - Refactor the `PubMedArticleClient` class to use the base client class.
# - Remove the pyright ignore directive.

import os
from xml.etree import (  # noqa: S405 (If we can't trust XML from NCBI we have bigger problems.)
    ElementTree,
)

import requests

from constants import PubMedConstants, RequestsConstants


class PubMedArticleClient:
    """Fetch a PubMed article's info."""

    def __init__(self, pmid: str) -> None:
        """Get info for the article."""
        self.pubmed_id = pmid
        self._data = None
        self.title = None

        # Fetch data populate the members.
        self._set_data()
        self._set_title()

    def _set_data(self) -> None:
        """Fetch the data from the PubMed API."""
        params = {
            "db": "pubmed",
            "id": self.pubmed_id,
            "retmode": "xml",
            "api_key": os.getenv("PUBMED_API_KEY"),
        }
        response = requests.get(
            url=PubMedConstants.API_URL,
            params=params,
            timeout=RequestsConstants.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        self._data = ElementTree.fromstring(response.text)  # noqa: S314 (If we can't trust XML from NCBI we have bigger problems.)

    def _set_title(self) -> None:
        """Extract the authors from the XML and set them."""
        self.title = self._data.find(
            ".//PubmedArticle/MedlineCitation/Article/ArticleTitle"
        ).text
