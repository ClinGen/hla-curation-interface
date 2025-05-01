"""Test PubMed article services."""

import pytest

from apps.publications.models.pubmed import PubMedArticle
from apps.publications.services.pubmed import (
    PubMedArticleService,
    PubMedArticleServiceError,
)


class MockPubMedArticleClient:
    """Mock the PubMed article client."""

    def __init__(self, pubmed_id: str) -> None:
        """Initialize the mock client."""
        self.pubmed_id = pubmed_id
        self.title = "article title"


@pytest.mark.component
@pytest.mark.django_db
def test_create_pubmed_article() -> None:
    """Make sure we can create a PubMed article."""
    pubmed_id = "123456789"
    client = MockPubMedArticleClient(pubmed_id)
    service = PubMedArticleService(client)  # type: ignore (We are using a mock client for our test.)
    article = service.create(pubmed_id)
    assert article is not None
    assert article.pubmed_id == client.pubmed_id
    assert article.title == client.title


@pytest.mark.component
@pytest.mark.django_db
def test_update_pubmed_article() -> None:
    """Make sure we can update a PubMed article."""
    pubmed_id = "987654321"
    PubMedArticle.objects.create(pubmed_id=pubmed_id, title="article title")
    client = MockPubMedArticleClient(pubmed_id)
    service = PubMedArticleService(client)  # type: ignore (We are using a mock client for our test.)
    service.update(pubmed_id, "new article title")
    article = PubMedArticle.objects.get(pubmed_id=pubmed_id)
    assert article is not None
    assert article.pubmed_id == client.pubmed_id
    assert article.title == "new article title"


@pytest.mark.component
@pytest.mark.django_db
def test_update_non_existent_pubmed_article() -> None:
    """Make sure we can't update a non-existent PubMed article."""
    pubmed_id = "000000000"
    client = MockPubMedArticleClient(pubmed_id)
    service = PubMedArticleService(client)  # type: ignore (We are using a mock client for our test.)
    with pytest.raises(PubMedArticleServiceError):
        service.update(pubmed_id, "new article title")
