"""Houses tests for the publication app."""

from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.models import UserProfile
from publication.models import Publication


class PublicationCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("publication-create")
        self.active_user = User.objects.create(
            username="ash",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        self.inactive_user = User.objects.create(
            username="misty",
            password="togepi",  # noqa: S106 (Hard-coded for testing.)
            is_active=False,
        )
        self.user_with_unverified_email = User.objects.create(
            username="brock",
            password="onix",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.user_with_unverified_email,
            firebase_email_verified=False,
        )
        self.user_who_can_create = User.objects.create(
            username="meowth",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            is_active=True,
        )
        UserProfile.objects.create(
            user=self.user_who_can_create,
            firebase_email_verified=True,
        )

    def test_redirects_anonymous_user_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_permission_denied_if_not_active(self):
        self.client.force_login(self.inactive_user)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_no_user_profile(self):
        self.client.force_login(self.active_user)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_permission_denied_if_email_not_verified(self):
        self.client.force_login(self.user_with_unverified_email)
        # If DEBUG is true, this will print a warning and a stack trace.
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_shows_radio_buttons(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_radio = (
            soup.find("label", {"for": "id_publication_type_0"}).get_text().strip()
        )
        self.assertIn("PubMed", pubmed_radio)
        biorxiv_radio = (
            soup.find("label", {"for": "id_publication_type_1"}).get_text().strip()
        )
        self.assertIn("bioRxiv", biorxiv_radio)
        medrxiv_radio = (
            soup.find("label", {"for": "id_publication_type_2"}).get_text().strip()
        )
        self.assertIn("medRxiv", medrxiv_radio)

    def test_shows_inputs(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_input = soup.find(id="id_pubmed_id")
        self.assertIsNotNone(pubmed_input)
        doi_input = soup.find(id="id_doi")
        self.assertIsNotNone(doi_input)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    @patch("publication.views.fetch_pubmed_data")
    def test_creates_pubmed_publication_with_valid_form_data(
        self, mock_fetch_pubmed_data: MagicMock
    ):
        self.client.force_login(self.user_who_can_create)
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "PUB", "pubmed_id": "123"}
        mock_pubmed_response = """
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
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
        """
        mock_fetch_pubmed_data.return_value = BeautifulSoup(mock_pubmed_response, "xml")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "PUB")  # type: ignore[union-attr]
        self.assertEqual(new_publication.pubmed_id, "123")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user_who_can_create)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Oak")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Common diseases in Pokémon")  # type: ignore[union-attr]

    @patch("publication.views.fetch_rxiv_data")
    def test_creates_biorxiv_publication_with_valid_form_data(
        self, mock_fetch_rxiv_data: MagicMock
    ):
        self.client.force_login(self.user_who_can_create)
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "BIO", "doi": "10.1101/123"}
        mock_fetch_rxiv_data.return_value = {
            "collection": [
                {
                    "title": "Common diseases in Pokémon",
                    "authors": "Oak, P.; Birch, P.",
                }
            ]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "BIO")  # type: ignore[union-attr]
        self.assertEqual(new_publication.doi, "10.1101/123")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user_who_can_create)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Oak, P.")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Common diseases in Pokémon")  # type: ignore[union-attr]

    @patch("publication.views.fetch_rxiv_data")
    def test_creates_medrxiv_publication_with_valid_form_data(
        self, mock_fetch_rxiv_data: MagicMock
    ):
        self.client.force_login(self.user_who_can_create)
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": "MED", "doi": "10.1101/456"}
        mock_fetch_rxiv_data.return_value = {
            "collection": [
                {
                    "title": "Diseases in Johto region Pokémon",
                    "authors": "Elm, P.; Juniper, P.",
                }
            ]
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publication.objects.count(), initial_publication_count + 1)
        new_publication = Publication.objects.first()
        self.assertIsNotNone(new_publication)
        self.assertEqual(new_publication.publication_type, "MED")  # type: ignore[union-attr]
        self.assertEqual(new_publication.doi, "10.1101/456")  # type: ignore[union-attr]
        self.assertEqual(new_publication.added_by, self.user_who_can_create)  # type: ignore[union-attr]
        self.assertEqual(new_publication.author, "Elm, P.")  # type: ignore[union-attr]
        self.assertEqual(new_publication.title, "Diseases in Johto region Pokémon")  # type: ignore[union-attr]

    def test_does_not_create_publication_with_invalid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_publication_count = Publication.objects.count()
        data = {"publication_type": ""}  # The publication_type field is required.
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "publication/create.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("pubmed_id", form.errors)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Publication.objects.count(), initial_publication_count)


class PublicationDetailTest(TestCase):
    fixtures = ["test_publications.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("publication-detail", kwargs={"pk": 1})

    def test_shows_publication_type(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        publication_type_image = soup.find("img", {"class": "entity-type-logo"})
        self.assertIn("PubMed", publication_type_image.attrs["alt"])

    def test_shows_title(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find(id="publication-title").get_text().strip()
        self.assertEqual(title, "Diseases in grass type Pokémon in the Kanto region")

    def test_shows_author(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        author = soup.find(id="author").get_text().strip()
        self.assertEqual(author, "Oak")

    def test_shows_pubmed_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pubmed_id = soup.find(id="pubmed-id").find("a").get_text().strip()
        self.assertEqual(pubmed_id, "123")

    def test_shows_doi(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        doi = soup.find(id="doi").find("a").get_text().strip()
        self.assertEqual(doi, "10.1000/123")

    def test_shows_date(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        date = soup.find(id="added-at").get_text().strip()
        self.assertEqual(date, "1990-01-01")

    def test_shows_search_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        search_button = soup.find(id="search-button").get_text().strip()
        self.assertIn("Search", search_button)

    def test_shows_add_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_button = soup.find(id="add-button").get_text().strip()
        self.assertIn("Add", add_button)


class PublicationSearchTest(TestCase):
    fixtures = ["test_publications.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("publication-search")

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_label = soup.find("label", {"for": "search-pk-input"}).get_text().strip()
        self.assertEqual(id_label, "ID")
        id_input = soup.find(id="search-pk-input")
        self.assertIsNotNone(id_input)

    def test_shows_type_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        type_label = (
            soup.find("label", {"for": "filter-publication-type-select"})
            .get_text()
            .strip()
        )
        self.assertEqual(type_label, "Type")
        type_select = soup.find(id="filter-publication-type-select")
        self.assertIsNotNone(type_select)

    def test_shows_author_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        author_label = (
            soup.find("label", {"for": "search-author-input"}).get_text().strip()
        )
        self.assertEqual(author_label, "Author")
        author_input = soup.find(id="search-author-input")
        self.assertIsNotNone(author_input)

    def test_shows_title_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        title_label = (
            soup.find("label", {"for": "search-title-input"}).get_text().strip()
        )
        self.assertEqual(title_label, "Title")
        title_input = soup.find(id="search-title-input")
        self.assertIsNotNone(title_input)

    def test_shows_added_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_label = (
            soup.find("label", {"for": "sort-added-at-button"}).get_text().strip()
        )
        self.assertEqual(added_label, "Added")
        added_button = soup.find(id="sort-added-at-button")
        self.assertIsNotNone(added_button)

    def test_shows_id_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        id_anchor = (
            soup.find("tbody").find("tr").find_all("td")[0].find("a").get_text().strip()
        )
        self.assertIn("1", id_anchor)

    def test_shows_type_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        publication_type = (
            soup.find("tbody")
            .find("tr")
            .find_all("td")[1]
            .find("span")
            .get_text()
            .strip()
        )
        self.assertIn("PubMed", publication_type)

    def test_shows_author_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        author = soup.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        self.assertEqual(author, "Oak")

    def test_shows_title_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("tbody").find("tr").find_all("td")[3].get_text().strip()
        self.assertEqual(title, "Diseases in grass type Pokémon in the Kanto region")

    def test_shows_added_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find("tbody").find("tr").find_all("td")[4].get_text().strip()
        self.assertIn("1990-01-01", added_at)
