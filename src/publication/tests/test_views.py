from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse

from auth_.models import UserProfile
from common.tests import ProtectedViewTestMixin, SuppressRequestLoggingMixin
from publication.clients import refresh_from_pubmed
from publication.models import Publication
from publication.views import REFRESH_FAILED_MESSAGE

MOCK_PUBMED_XML = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <Article>
        <ArticleTitle>Common diseases in Pokémon</ArticleTitle>
        <AuthorList CompleteYN="Y">
          <Author ValidYN="Y">
            <LastName>Oak</LastName>
          </Author>
          <Author ValidYN="Y">
            <LastName>Birch</LastName>
          </Author>
        </AuthorList>
      </Article>
      <PubDate>
        <Year>1999</Year>
      </PubDate>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


class PublicationCreateTest(ProtectedViewTestMixin, TestCase):
    url = reverse("publication-create")
    template = "publication/create.html"
    page_name = "Add Publication"
    expected_text = [
        "Add Publication",
        "PubMed ID",
        (
            "Do not use PubMed IDs of preprint articles, only enter PubMed IDs of "
            "peer-reviewed publications."
        ),
        "Submit",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_has_no_preprint_inputs(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, 'name="publication_type"')
        self.assertNotContains(response, 'name="doi"')
        self.assertNotContains(response, "bioRxiv Paper")
        self.assertNotContains(response, "medRxiv Paper")

    @patch("publication.clients.fetch_pubmed_data")
    def test_creates_pubmed_publication_with_valid_form_data(
        self, mock_fetch_pubmed_data: MagicMock
    ):
        initial_publication_count = Publication.objects.count()
        data = {"pubmed_id": "123"}
        mock_fetch_pubmed_data.return_value = BeautifulSoup(MOCK_PUBMED_XML, "xml")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        assert new_publication is not None
        self.assertEqual(new_publication.pubmed_id, "123")
        self.assertEqual(new_publication.added_by, self.user4_yes_phi_yes_perms)
        self.assertEqual(new_publication.author, "Oak")
        self.assertEqual(new_publication.authors, "Oak; Birch")
        self.assertEqual(new_publication.title, "Common diseases in Pokémon")
        self.assertEqual(new_publication.publication_year, 1999)

    def test_does_not_create_publication_with_invalid_form_data(self):
        initial_publication_count = Publication.objects.count()
        data = {"pubmed_id": ""}  # The pubmed_id field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "publication/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("pubmed_id", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Publication.objects.count(), initial_publication_count)

    @patch("publication.clients.fetch_pubmed_data")
    def test_does_not_create_preprint_publication(
        self, mock_fetch_pubmed_data: MagicMock
    ):
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "BIO", "doi": "10.1101/123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("pubmed_id", response.context["form"].errors)
        self.assertEqual(Publication.objects.count(), initial_publication_count)
        mock_fetch_pubmed_data.assert_not_called()


class PublicationDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_publications.json"]
    url = reverse("publication-detail", kwargs={"slug": "P000001"})
    template = "publication/detail.html"
    page_name = "P000001 Details"
    expected_text = [
        "Diseases in grass type Pokémon in the Kanto region",
        "Oak",
        "Oak S; Juniper N",
        "123",
        "1990-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_shows_placeholder_without_authors(self):
        Publication.objects.filter(slug="P000001").update(authors="")
        response = self.client.get(self.url)
        self.assertContains(response, "<td>Authors</td>", html=False)
        self.assertNotContains(response, "Oak S; Juniper N")
        self.assertContains(response, "<td>------</td>", html=True)


class PublicationListTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_publications.json"]
    url = reverse("publication-list")
    template = "publication/list.html"
    page_name = "Publication Search"
    expected_text = [
        "ID",
        "Title",
        "Author",
        "Year",
        "PMID",
        "Updated",
        "P000001",
        "Diseases in grass type Pokémon in the Kanto region",
        "Oak",
        "123",
        "1990-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_search_matches_a_non_primary_author(self):
        response = self.client.get(self.url, {"q": "Juniper"})
        self.assertContains(response, "P000001")
        self.assertContains(response, "1 result")

    def test_search_with_no_match_returns_zero_results(self):
        response = self.client.get(self.url, {"q": "zzz_no_match"})
        self.assertContains(response, "0 results")
        self.assertNotContains(response, "P000001")


class RefreshFromPubMedTest(TestCase):
    fixtures = ["test_publications.json"]

    def setUp(self):
        self.publication = Publication.objects.get(slug="P000001")

    @patch("publication.clients.fetch_pubmed_data")
    def test_sets_every_pubmed_field(self, mock_fetch_pubmed_data: MagicMock):
        mock_fetch_pubmed_data.return_value = BeautifulSoup(MOCK_PUBMED_XML, "xml")
        self.assertTrue(refresh_from_pubmed(self.publication))
        mock_fetch_pubmed_data.assert_called_once_with(self.publication.pubmed_id)
        self.assertEqual(self.publication.title, "Common diseases in Pokémon")
        self.assertEqual(self.publication.author, "Oak")
        self.assertEqual(self.publication.authors, "Oak; Birch")
        self.assertEqual(self.publication.publication_year, 1999)

    @patch("publication.clients.fetch_pubmed_data", return_value=None)
    def test_failure_changes_nothing(self, _mock_fetch_pubmed_data: MagicMock):
        before = model_to_dict(self.publication)
        self.assertFalse(refresh_from_pubmed(self.publication))
        self.assertEqual(model_to_dict(self.publication), before)


def _make_user(username: str, *, can_curate: bool) -> User:
    user = User.objects.create(username=username)
    UserProfile.objects.create(
        user=user,
        has_signed_phi_agreement=True,
        has_curation_permissions=can_curate,
    )
    return user


class PublicationRefreshTest(SuppressRequestLoggingMixin, TestCase):
    fixtures = ["test_publications.json"]
    url = reverse("publication-refresh", kwargs={"slug": "P000001"})
    detail_url = reverse("publication-detail", kwargs={"slug": "P000001"})

    def setUp(self):
        self.client.force_login(_make_user("curator", can_curate=True))

    def _publication(self) -> Publication:
        return Publication.objects.get(slug="P000001")

    @patch("publication.clients.fetch_pubmed_data")
    def test_post_refreshes_and_redirects(self, mock_fetch_pubmed_data: MagicMock):
        mock_fetch_pubmed_data.return_value = BeautifulSoup(MOCK_PUBMED_XML, "xml")
        history_count = self._publication().history.count()  # type: ignore
        response = self.client.post(self.url)
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertEqual(self._publication().authors, "Oak; Birch")
        self.assertEqual(
            self._publication().history.count(),  # type: ignore
            history_count + 1,
        )

    @patch("publication.clients.fetch_pubmed_data", return_value=None)
    def test_failure_warns_and_changes_nothing(
        self, _mock_fetch_pubmed_data: MagicMock
    ):
        before = model_to_dict(self._publication())
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(model_to_dict(self._publication()), before)
        self.assertContains(response, REFRESH_FAILED_MESSAGE)

    @patch("publication.clients.fetch_pubmed_data")
    def test_get_does_not_refresh(self, mock_fetch_pubmed_data: MagicMock):
        response = self.client.get(self.url)
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        mock_fetch_pubmed_data.assert_not_called()

    @patch("publication.clients.fetch_pubmed_data")
    def test_post_without_curation_permissions_is_forbidden(
        self, mock_fetch_pubmed_data: MagicMock
    ):
        self.client.force_login(_make_user("viewer", can_curate=False))
        with self.suppress_request_logging():
            response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        mock_fetch_pubmed_data.assert_not_called()

    def test_anonymous_post_redirects_to_login(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("next=", response["Location"])

    def test_detail_page_has_confirmed_refresh_button(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, f'action="{self.url}"')
        self.assertContains(response, "data-confirm=")
        self.assertContains(response, "Refresh from PubMed")
