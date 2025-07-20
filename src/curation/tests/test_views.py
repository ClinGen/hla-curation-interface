"""Houses tests for the curation app's views."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from core.models import UserProfile
from curation.models import Curation, Evidence, Status
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication


class CurationCreateTest(TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("curation-create")
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

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        breadcrumb = soup.find("nav", {"class": "breadcrumb"})
        self.assertIsNotNone(breadcrumb)

    def test_shows_radio_buttons(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_radio_button = soup.find(id="id_curation_type_0")
        self.assertIsNotNone(allele_radio_button)
        haplotype_radio_button = soup.find(id="id_curation_type_1")
        self.assertIsNotNone(haplotype_radio_button)

    def test_shows_allele_select(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele_select = soup.find(id="id_allele")
        self.assertIsNotNone(allele_select)

    def test_shows_disease_select(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        disease_select = soup.find(id="id_disease")
        self.assertIsNotNone(disease_select)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"})
        self.assertIsNotNone(submit_button)

    def test_creates_allele_curation_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "ALL", "allele": "1", "disease": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        self.assertIsNotNone(new_curation)
        self.assertEqual(new_curation.curation_type, "ALL")  # type: ignore[union-attr]
        self.assertEqual(new_curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.disease, Disease.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.added_by, self.user_who_can_create)  # type: ignore[union-attr]

    def test_creates_haplotype_curation_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "HAP", "haplotype": "1", "disease": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        self.assertIsNotNone(new_curation)
        self.assertEqual(new_curation.curation_type, "HAP")  # type: ignore[union-attr]
        self.assertEqual(new_curation.haplotype, Haplotype.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.disease, Disease.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.added_by, self.user_who_can_create)  # type: ignore[union-attr]


class CurationDetailTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("curation-detail", kwargs={"curation_pk": 1})

    def test_shows_breadcrumb(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        breadcrumb = soup.find("nav", {"class": "breadcrumb"})
        self.assertIsNotNone(breadcrumb)

    def test_shows_allele_name(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele = soup.find(id="allele").get_text().strip()
        self.assertEqual(allele, "A*01:02:03")

    def test_shows_disease_name(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele = soup.find(id="disease").get_text().strip()
        self.assertEqual(allele, "acute oran berry intoxication")

    def test_shows_status(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        status = soup.find(id="status").get_text().strip()
        self.assertEqual(status, "In Progress")

    def test_shows_classification(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        classification = soup.find(id="classification").get_text().strip()
        self.assertEqual(classification, "Limited")

    def test_shows_score(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        score = soup.find(id="score").get_text().strip()
        self.assertIsNotNone(score)

    def test_shows_curation_id(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        curation_id = soup.find(id="curation-id").get_text().strip()
        self.assertEqual(curation_id, "1")

    def test_shows_added_at(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="added-at").get_text().strip()
        self.assertEqual(added_at, "1970-01-01")

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

    def test_shows_edit_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        edit_button = soup.find(id="edit-evidence-button").get_text().strip()
        self.assertIn("Edit", edit_button)

    def test_shows_add_evidence_button(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_evidence_button = soup.find(id="add-evidence-button").get_text().strip()
        self.assertIn("Add Evidence", add_evidence_button)

    def test_shows_id_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        id_th = (
            evidence_table.find("thead").find("tr").find_all("th")[0].get_text().strip()
        )
        self.assertEqual(id_th, "ID")

    def test_shows_publication_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        publication_th = (
            evidence_table.find("thead").find("tr").find_all("th")[1].get_text().strip()
        )
        self.assertEqual(publication_th, "Publication")

    def test_shows_needs_review_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        needs_review_th = (
            evidence_table.find("thead").find("tr").find_all("th")[2].get_text().strip()
        )
        self.assertEqual(needs_review_th, "Needs Review")

    def test_shows_status_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        status_th = (
            evidence_table.find("thead").find("tr").find_all("th")[3].get_text().strip()
        )
        self.assertEqual(status_th, "Status")

    def test_shows_conflicting_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        conflicting_th = (
            evidence_table.find("thead").find("tr").find_all("th")[4].get_text().strip()
        )
        self.assertEqual(conflicting_th, "Conflicting")

    def test_shows_included_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        included_th = (
            evidence_table.find("thead").find("tr").find_all("th")[5].get_text().strip()
        )
        self.assertEqual(included_th, "Included")

    def test_shows_score_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        score_th = (
            evidence_table.find("thead").find("tr").find_all("th")[6].get_text().strip()
        )
        self.assertEqual(score_th, "Score")

    def test_shows_id_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        id_anchor = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[0]
            .find("a")
            .get_text()
            .strip()
        )
        self.assertIn("1", id_anchor)

    def test_shows_publication_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        publication_anchor = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[1]
            .find("a")
            .get_text()
            .strip()
        )
        title = "Diseases in grass type Pokémon in the Kanto region"
        self.assertIn(title, publication_anchor)

    def test_shows_needs_review_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        needs_review = (
            evidence_table.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        )
        self.assertEqual(needs_review, "False")

    def test_shows_status_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        status = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[3]
            .find("span")
            .get_text()
            .strip()
        )
        self.assertEqual(status, "In Progress")

    def test_shows_conflicting_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        conflicting = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[4]
            .find("label")
            .find("input")
        )
        self.assertIsNotNone(conflicting)

    def test_shows_included_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        included = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[5]
            .find("label")
            .find("input")
        )
        self.assertIsNotNone(included)

    def test_shows_score_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        score = (
            evidence_table.find("tbody").find("tr").find_all("td")[6].get_text().strip()
        )
        self.assertEqual(score, "2.0")


class CurationSearchTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json", "test_curations.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("curation-search")

    def test_shows_breadcrumb(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        breadcrumb = soup.find("nav", {"class": "breadcrumb"})
        self.assertIsNotNone(breadcrumb)

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
            soup.find("label", {"for": "filter-curation-type-select"})
            .get_text()
            .strip()
        )
        self.assertEqual(type_label, "Type")
        type_select = soup.find(id="filter-curation-type-select")
        self.assertIsNotNone(type_select)

    def test_shows_allele_name_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_label = (
            soup.find("label", {"for": "search-allele-name-input"}).get_text().strip()
        )
        self.assertEqual(name_label, "Allele")
        name_input = soup.find(id="search-allele-name-input")
        self.assertIsNotNone(name_input)

    def test_shows_haplotype_name_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_label = (
            soup.find("label", {"for": "search-haplotype-name-input"})
            .get_text()
            .strip()
        )
        self.assertEqual(name_label, "Haplotype")
        name_input = soup.find(id="search-haplotype-name-input")
        self.assertIsNotNone(name_input)

    def test_shows_disease_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        disease_label = (
            soup.find("label", {"for": "search-disease-name-input"}).get_text().strip()
        )
        self.assertEqual(disease_label, "Disease")
        disease_input = soup.find(id="search-disease-name-input")
        self.assertIsNotNone(disease_input)

    def test_shows_score_in_thead(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        status_label = (
            soup.find("label", {"for": "filter-status-select"}).get_text().strip()
        )
        self.assertEqual(status_label, "Status")
        status_select = soup.find(id="filter-status-select")
        self.assertIsNotNone(status_select)

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
        curation_type = (
            soup.find("tbody")
            .find("tr")
            .find_all("td")[1]
            .find("span")
            .get_text()
            .strip()
        )
        self.assertIn("Allele", curation_type)

    def test_shows_allele_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        self.assertIn("A*01:02:03", name)

    def test_shows_haplotype_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name = soup.find("tbody").find("tr").find_all("td")[3].get_text().strip()
        self.assertIn("--", name)

    def test_shows_disease_name_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        disease = soup.find("tbody").find("tr").find_all("td")[4].get_text().strip()
        self.assertEqual("acute oran berry intoxication", disease)

    def test_shows_score_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        status = soup.find("tbody").find("tr").find_all("td")[5].get_text().strip()
        self.assertEqual(status, "In Progress")

    def test_shows_added_in_tbody(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find("tbody").find("tr").find_all("td")[6].get_text().strip()
        self.assertIn("1970-01-01", added_at)


class CurationEditEvidenceTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("curation-edit-evidence", kwargs={"curation_pk": 1})
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

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        breadcrumb = soup.find("nav", {"class": "breadcrumb"})
        self.assertIsNotNone(breadcrumb)

    def test_shows_allele_name(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele = soup.find(id="allele").get_text().strip()
        self.assertEqual(allele, "A*01:02:03")

    def test_shows_disease_name(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        allele = soup.find(id="disease").get_text().strip()
        self.assertEqual(allele, "acute oran berry intoxication")

    def test_shows_status(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        status = soup.find(id="status").get_text().strip()
        self.assertEqual(status, "In Progress")

    def test_shows_classification(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        classification = soup.find(id="classification").get_text().strip()
        self.assertEqual(classification, "Limited")

    def test_shows_score(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        score = soup.find(id="score").get_text().strip()
        self.assertIsNotNone(score)

    def test_shows_curation_id(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        curation_id = soup.find(id="curation-id").get_text().strip()
        self.assertEqual(curation_id, "1")

    def test_shows_added_at(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        added_at = soup.find(id="added-at").get_text().strip()
        self.assertEqual(added_at, "1970-01-01")

    def test_shows_search_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        search_button = soup.find(id="search-button").get_text().strip()
        self.assertIn("Search", search_button)

    def test_shows_add_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        add_button = soup.find(id="add-button").get_text().strip()
        self.assertIn("Add", add_button)

    def test_shows_save_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        save_button = soup.find(id="save-edit-button")
        self.assertIsNotNone(save_button)

    def test_shows_cancel_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        cancel_button = soup.find(id="cancel-edit-button")
        self.assertIsNotNone(cancel_button)

    def test_shows_id_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        id_th = (
            evidence_table.find("thead").find("tr").find_all("th")[0].get_text().strip()
        )
        self.assertEqual(id_th, "ID")

    def test_shows_publication_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        publication_th = (
            evidence_table.find("thead").find("tr").find_all("th")[1].get_text().strip()
        )
        self.assertEqual(publication_th, "Publication")

    def test_shows_needs_review_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        needs_review_th = (
            evidence_table.find("thead").find("tr").find_all("th")[2].get_text().strip()
        )
        self.assertEqual(needs_review_th, "Needs Review")

    def test_shows_status_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        status_th = (
            evidence_table.find("thead").find("tr").find_all("th")[3].get_text().strip()
        )
        self.assertEqual(status_th, "Status")

    def test_shows_conflicting_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        conflicting_th = (
            evidence_table.find("thead").find("tr").find_all("th")[4].get_text().strip()
        )
        self.assertEqual(conflicting_th, "Conflicting")

    def test_shows_included_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        included_th = (
            evidence_table.find("thead").find("tr").find_all("th")[5].get_text().strip()
        )
        self.assertEqual(included_th, "Included")

    def test_shows_score_in_thead(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        score_th = (
            evidence_table.find("thead").find("tr").find_all("th")[6].get_text().strip()
        )
        self.assertEqual(score_th, "Score")

    def test_shows_id_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        id_anchor = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[0]
            .find("a")
            .get_text()
            .strip()
        )
        self.assertIn("1", id_anchor)

    def test_shows_publication_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        publication_anchor = (
            evidence_table.find("tbody")
            .find("tr")
            .find_all("td")[1]
            .find("a")
            .get_text()
            .strip()
        )
        title = "Diseases in grass type Pokémon in the Kanto region"
        self.assertIn(title, publication_anchor)

    def test_shows_needs_review_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        needs_review = (
            evidence_table.find("tbody").find("tr").find_all("td")[2].get_text().strip()
        )
        self.assertEqual(needs_review, "False")

    def test_shows_status_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        status = (
            evidence_table.find("tbody").find("tr").find_all("td")[3].find("select")
        )
        self.assertIsNotNone(status)

    def test_shows_conflicting_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        conflicting = (
            evidence_table.find("tbody").find("tr").find_all("td")[4].find("input")
        )
        self.assertIsNotNone(conflicting)

    def test_shows_included_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        included = (
            evidence_table.find("tbody").find("tr").find_all("td")[5].find("input")
        )
        self.assertIsNotNone(included)

    def test_shows_score_in_tbody(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        evidence_table = soup.find(id="evidence-table")
        score = (
            evidence_table.find("tbody").find("tr").find_all("td")[6].get_text().strip()
        )
        self.assertEqual(score, "2.0")


class EvidenceCreateTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("evidence-create", kwargs={"curation_pk": 1})
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

    def test_shows_publication_input(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        publication_input = soup.find(id="id_publication")
        self.assertIsNotNone(publication_input)

    def test_shows_submit_button(self):
        self.client.force_login(self.user_who_can_create)
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        submit_button = soup.find("button", {"type": "submit"}).get_text().strip()
        self.assertEqual(submit_button, "Submit")

    def test_creates_evidence_with_valid_form_data(self):
        self.client.force_login(self.user_who_can_create)
        initial_evidence_count = Evidence.objects.count()
        data = {"publication": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evidence.objects.count(), initial_evidence_count + 1)
        new_evidence = Evidence.objects.first()
        self.assertIsNotNone(new_evidence)
        self.assertEqual(new_evidence.curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_evidence.curation.disease, Disease.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_evidence.publication, Publication.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertFalse(new_evidence.needs_review)  # type: ignore[union-attr]
        self.assertEqual(new_evidence.status, Status.IN_PROGRESS)  # type: ignore[union-attr]
        self.assertEqual(new_evidence.added_by, self.user_who_can_create)  # type: ignore[union-attr]


class EvidenceDetailTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "evidence-detail", kwargs={"curation_pk": 1, "evidence_pk": 1}
        )

    def test_shows_menu(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        menu = soup.find(id="menu")
        self.assertIsNotNone(menu)

    def test_shows_evidence_data_table(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(id="evidence-data-table")
        self.assertIsNotNone(table)

    def test_shows_evidence_score_table(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(id="evidence-score-table")
        self.assertIsNotNone(table)

    def test_shows_total_score(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        total_score = soup.find(id="total-score").find("b").get_text().strip()
        self.assertIsNotNone(total_score)


class EvidenceEditTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.client = Client()
        self.url = reverse("evidence-edit", kwargs={"curation_pk": 1, "evidence_pk": 1})

    def test_shows_menu(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        menu = soup.find(id="menu")
        self.assertIsNotNone(menu)

    def test_shows_data_headings(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        heading_ids = [
            "gwas",
            "zygosity",
            "phase",
            "typing-method",
            "demographics",
            "multiple-testing-correction",
            "effect-size",
            "confidence-interval",
            "cohort-size",
            "significant-association",
            "needs-review",
            "save",
        ]
        for heading_id in heading_ids:
            heading = soup.find(id=heading_id)
            self.assertIsNotNone(heading)
