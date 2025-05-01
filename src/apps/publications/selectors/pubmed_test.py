"""Test PubMed selectors."""

import pytest

from apps.publications.models.pubmed import PubMedArticle
from apps.publications.selectors.pubmed import PubMedArticleSelector


@pytest.mark.component
@pytest.mark.django_db
def test_get_existing_pubmed_article() -> None:
    """Make sure we can get an existing PubMed article."""
    PubMedArticle.objects.create(pubmed_id="123456789", title="Test Article")
    selector = PubMedArticleSelector()
    retrieved_article = selector.get(human_readable_id="123456789")
    assert retrieved_article is not None
    assert retrieved_article.pubmed_id == "123456789"
    assert retrieved_article.title == "Test Article"


@pytest.mark.component
@pytest.mark.django_db
def test_get_non_existent_pubmed_article() -> None:
    """Make sure we can't get a non-existing PubMed article."""
    selector = PubMedArticleSelector()
    retrieved_article = selector.get(human_readable_id="999")
    assert retrieved_article is None


@pytest.mark.component
@pytest.mark.django_db
def test_list_pubmed_articles_with_no_query() -> None:
    """Make sure we can list all PubMed articles."""
    PubMedArticle.objects.create(pubmed_id="123456789", title="Test Article A")
    PubMedArticle.objects.create(pubmed_id="987654321", title="Test Article B")
    selector = PubMedArticleSelector()
    articles = selector.list()
    assert articles is not None
    assert len(articles) == 2
    assert articles[0].pubmed_id == "123456789"
    assert articles[0].title == "Test Article A"
    assert articles[1].pubmed_id == "987654321"
    assert articles[1].title == "Test Article B"


@pytest.mark.component
@pytest.mark.django_db
def test_list_pubmed_articles_with_pubmed_id_query() -> None:
    """Make sure we can list a subset of PubMed articles filtered by PubMed ID."""
    PubMedArticle.objects.create(pubmed_id="111111111", title="Test Article A")
    PubMedArticle.objects.create(pubmed_id="122222222", title="Test Article B")
    PubMedArticle.objects.create(pubmed_id="333333333", title="Test Article C")
    selector = PubMedArticleSelector()
    articles = selector.list("1")
    assert articles is not None
    assert len(articles) == 2
    assert articles[0].pubmed_id == "111111111"
    assert articles[0].title == "Test Article A"
    assert articles[1].pubmed_id == "122222222"
    assert articles[1].title == "Test Article B"


@pytest.mark.component
@pytest.mark.django_db
def test_list_pubmed_articles_with_title_query() -> None:
    """Make sure we can list a subset of PubMed articles filtered by title."""
    PubMedArticle.objects.create(
        pubmed_id="111111111", title="Title with a common word A"
    )
    PubMedArticle.objects.create(
        pubmed_id="222222222", title="Title with a common word B"
    )
    PubMedArticle.objects.create(
        pubmed_id="333333333", title="This is a totally different title"
    )
    selector = PubMedArticleSelector()
    articles = selector.list("common")
    assert articles is not None
    assert len(articles) == 2
    assert articles[0].pubmed_id == "111111111"
    assert articles[0].title == "Title with a common word A"
    assert articles[1].pubmed_id == "222222222"
    assert articles[1].title == "Title with a common word B"
