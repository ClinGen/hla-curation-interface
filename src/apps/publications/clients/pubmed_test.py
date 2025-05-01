"""Test PubMed service."""

import pytest

from apps.publications.clients.pubmed import PubMedArticleClient


@pytest.mark.contract
def test_client() -> None:
    """Make sure we can get info about an article from PubMed."""
    pmid = "10446108"
    title = "HLA-DR and -DQ phenotypes in inflammatory bowel disease: a meta-analysis."
    article = PubMedArticleClient(pmid)
    assert isinstance(article.title, str)
    assert article.title == title
