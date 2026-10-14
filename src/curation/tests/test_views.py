"""Houses tests for the curation app's views."""

from datetime import date, timedelta
from unittest.mock import PropertyMock, patch

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from allele.models import Allele
from auth_.models import UserProfile
from common.tests import (
    ProtectedViewTestMixin,
    SuppressRequestLoggingMixin,
    field_block,
)
from curation.constants.models.common import Status
from curation.constants.models.curation import (
    HLA_CURATION_TASKFORCE_ID,
    TASKFORCE_CHOICES,
    Classification,
    CurationTypes,
)
from curation.constants.models.evidence import (
    AdditionalPhenotypes,
    EffectSizeStatistic,
    MultipleTestingCorrection,
    TypingMethod,
    Zygosity,
)
from curation.models import (
    Curation,
    Demographic,
    Evidence,
)
from curation.summary import build_evidence_summary
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication
from repo.models import PublishedCuration


class CurationCreateTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_haplotypes.json",
        "test_diseases.json",
        "test_publications.json",
    ]
    url = reverse("curation-create")
    template = "curation/create.html"
    page_name = "Add Curation"
    expected_text = [
        "Add Curation",
        "Curation Type",
        "Allele",
        "Haplotype",
        "Disease",
        "Submit",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_creates_allele_curation_with_valid_form_data(self):
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "ALL", "allele": "1", "disease": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        assert new_curation is not None
        self.assertEqual(new_curation.curation_type, "ALL")
        self.assertEqual(new_curation.allele, Allele.objects.get(pk=1))
        self.assertEqual(new_curation.disease, Disease.objects.get(pk=1))
        self.assertEqual(new_curation.added_by, self.user4_yes_phi_yes_perms)

    def test_creates_haplotype_curation_with_valid_form_data(self):
        initial_curation_count = Curation.objects.count()
        data = {"curation_type": "HAP", "haplotype": "1", "disease": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Curation.objects.count(), initial_curation_count + 1)
        new_curation = Curation.objects.first()
        assert new_curation is not None
        self.assertEqual(new_curation.curation_type, "HAP")
        self.assertEqual(new_curation.haplotype, Haplotype.objects.get(pk=1))
        self.assertEqual(new_curation.disease, Disease.objects.get(pk=1))
        self.assertEqual(new_curation.added_by, self.user4_yes_phi_yes_perms)

    def _make_existing(
        self, curation_type: str, *, with_evidence: bool = True, **kwargs
    ) -> Curation:
        if curation_type == CurationTypes.ALLELE:
            target = {"allele": Allele.objects.get(pk=1)}
        else:
            target = {"haplotype": Haplotype.objects.get(pk=1)}
        curation = Curation.objects.create(
            curation_type=curation_type,
            disease=Disease.objects.get(pk=1),
            **target,
            **kwargs,
        )
        if with_evidence:
            Evidence.objects.create(
                curation=curation, publication=Publication.objects.get(pk=1)
            )
        return curation

    def _data(self, curation_type: str, **extra) -> dict[str, str]:
        field = "allele" if curation_type == CurationTypes.ALLELE else "haplotype"
        return {"curation_type": curation_type, field: "1", "disease": "1", **extra}

    def test_one_existing_pair_requires_confirmation(self):
        for curation_type in (CurationTypes.ALLELE, CurationTypes.HAPLOTYPE):
            with self.subTest(curation_type=curation_type):
                existing = self._make_existing(curation_type)
                count = Curation.objects.count()
                response = self.client.post(self.url, self._data(curation_type))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Curation.objects.count(), count)
                self.assertContains(response, existing.slug)
                self.assertContains(response, 'name="confirm_duplicate"')

    def test_one_existing_pair_allows_creation_after_confirmation(self):
        for curation_type in (CurationTypes.ALLELE, CurationTypes.HAPLOTYPE):
            with self.subTest(curation_type=curation_type):
                self._make_existing(curation_type)
                count = Curation.objects.count()
                data = self._data(curation_type, confirm_duplicate="on")
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(Curation.objects.count(), count + 1)

    def test_one_existing_pair_without_evidence_blocks_creation(self):
        for curation_type in (CurationTypes.ALLELE, CurationTypes.HAPLOTYPE):
            with self.subTest(curation_type=curation_type):
                existing = self._make_existing(curation_type, with_evidence=False)
                count = Curation.objects.count()
                data = self._data(curation_type, confirm_duplicate="on")
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Curation.objects.count(), count)
                self.assertContains(response, existing.slug)
                self.assertNotContains(response, 'name="confirm_duplicate"')
                existing.delete()

    def test_two_existing_pairs_block_creation(self):
        for curation_type in (CurationTypes.ALLELE, CurationTypes.HAPLOTYPE):
            with self.subTest(curation_type=curation_type):
                first = self._make_existing(curation_type)
                second = self._make_existing(curation_type)
                count = Curation.objects.count()
                data = self._data(curation_type, confirm_duplicate="on")
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Curation.objects.count(), count)
                self.assertContains(response, first.slug)
                self.assertContains(response, second.slug)
                self.assertNotContains(response, 'name="confirm_duplicate"')

    def test_published_curation_and_its_copy_count_as_one_pair(self):
        published = self._make_existing(CurationTypes.ALLELE, status=Status.PUBLISHED)
        copy = self._make_existing(CurationTypes.ALLELE, copied_from=published)
        data = self._data(CurationTypes.ALLELE, confirm_duplicate="on")
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Curation.objects.exclude(pk__in=[published.pk, copy.pk]).count(), 1
        )

    def test_same_allele_with_different_disease_is_not_flagged(self):
        self._make_existing(CurationTypes.ALLELE)
        data = {"curation_type": CurationTypes.ALLELE, "allele": "1", "disease": "2"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)


class CurationDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]
    url = reverse("curation-detail", kwargs={"curation_slug": "C000001"})
    template = "curation/detail.html"
    page_name = "C000001 Details"
    expected_text = [
        "C000001",
        "A*01:02:03",
        "acute oran berry intoxication",
        "In Progress",
        "1970-01-01",
        "ID",
        "Publication",
        "Needs Review",
        "Status",
        "Included",
        "Score",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_shows_evidence_in_tbody(self):
        response = self.client.get(self.url)
        self.assertContains(response, "E000001")
        self.assertContains(
            response, "Diseases in grass type Pokémon in the Kanto region"
        )
        self.assertContains(response, "0.0")  # Should default to a score of 0.0.

    def test_shows_taskforce_review_date_when_set(self):
        curation = Curation.objects.get(slug="C000001")
        curation.taskforce_review_date = date(2026, 9, 1)
        curation.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Review Date")
        self.assertContains(response, "2026-09-01")

    def test_shows_feedback_after_send_back_without_classification(self):
        curation = Curation.objects.get(slug="C000001")
        curation.taskforce_additional_notes = "Please add the replication cohort."
        curation.taskforce = HLA_CURATION_TASKFORCE_ID
        curation.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Sent Back for Revision")
        self.assertContains(response, "Please add the replication cohort.")
        self.assertContains(
            response, dict(TASKFORCE_CHOICES)[HLA_CURATION_TASKFORCE_ID]
        )

    def test_shows_evidence_summary_after_approval(self):
        curation = Curation.objects.get(slug="C000001")
        curation.status = Status.APPROVED
        curation.taskforce_classification = Classification.MODERATE
        curation.taskforce_evidence_summary = "Consistent association."
        curation.save()
        response = self.client.get(self.url)
        self.assertContains(response, "Taskforce Review")
        self.assertContains(response, "Evidence Summary")
        self.assertContains(response, "Consistent association.")
        self.assertNotContains(response, "Classification Notes")
        self.assertNotContains(response, "Sent Back for Revision")
        self.assertContains(response, 'class="message mt-2"')
        self.assertContains(
            response, '<h3 class="title is-6 mb-1">Evidence Summary</h3>', html=True
        )

    def test_feedback_items_are_headings_not_a_list(self):
        curation = Curation.objects.get(slug="C000001")
        curation.status = Status.APPROVED
        curation.taskforce = HLA_CURATION_TASKFORCE_ID
        curation.taskforce_classification = Classification.MODERATE
        curation.taskforce_override_reason = "Replicated twice."
        curation.taskforce_evidence_summary = "Consistent association."
        curation.save()
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        feedback = soup.select_one(".taskforce-feedback")
        assert feedback is not None
        self.assertIsNone(feedback.find("ul"))
        self.assertEqual(
            [heading.get_text(strip=True) for heading in feedback.find_all("h3")],
            [
                "Taskforce",
                "Classification",
                "Suggested Classification Override Reason",
                "Evidence Summary",
            ],
        )
        override = feedback.find(
            "h3", string="Suggested Classification Override Reason"
        )
        assert override is not None
        paragraph = override.find_next_sibling("p")
        assert paragraph is not None
        self.assertEqual(paragraph.get_text(strip=True), "Replicated twice.")

    def test_summary_table_has_no_id_row(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        labels = [
            row.td.get_text(strip=True)
            for row in soup.select(".table-container table tr")
            if row.td
        ]
        self.assertIn("Allele", labels)
        self.assertNotIn("HCI Curation ID", labels)
        breadcrumb = soup.select_one(".breadcrumb")
        assert breadcrumb is not None
        self.assertIn("C000001 Details", breadcrumb.get_text(" ", strip=True))

    def test_shows_no_feedback_panel_without_feedback(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "Taskforce Review")
        self.assertNotContains(response, "Sent Back for Revision")

    def test_shows_no_classification_set_when_score_is_zero(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No Classification Set")
        self.assertNotContains(response, "Suggested Classification")


class CurationEditEvidenceTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]
    url = reverse("curation-edit-evidence", kwargs={"curation_slug": "C000001"})
    template = "curation/edit/evidence.html"
    page_name = "Edit Evidence"
    expected_text = [
        "Edit Evidence",
        "Status",
        "Included",
        "Save",
        "Cancel",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


class CurationListTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json", "test_curations.json"]
    url = reverse("curation-list")
    template = "curation/list.html"
    page_name = "Curation Search"
    expected_text = [
        "ID",
        "Type",
        "Allele",
        "Haplotype",
        "Disease",
        "Status",
        "Classification",
        "Updated",
        "C000001",
        "A*01:02:03",
        "acute oran berry intoxication",
        "In Progress",
        "bi-cone-striped",
        "No Classification Set",
        "1970-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_status_uses_the_common_tag_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "common/tags/in_progress.html")


class EvidenceCreateTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
    ]
    url = reverse("evidence-create", kwargs={"curation_slug": "C000001"})
    template = "evidence/create.html"
    page_name = "Add Evidence"
    expected_text = ["Add Evidence", "Publication", "Submit"]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_creates_evidence_with_valid_form_data(self):
        initial_evidence_count = Evidence.objects.count()
        data = {"publication": "1"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evidence.objects.count(), initial_evidence_count + 1)
        new_evidence = Evidence.objects.first()
        assert new_evidence is not None
        self.assertEqual(new_evidence.curation.allele, Allele.objects.get(pk=1))
        self.assertEqual(new_evidence.curation.disease, Disease.objects.get(pk=1))
        self.assertEqual(new_evidence.publication, Publication.objects.get(pk=1))
        self.assertTrue(new_evidence.needs_review)
        self.assertEqual(new_evidence.status, Status.IN_PROGRESS)
        self.assertEqual(new_evidence.added_by, self.user4_yes_phi_yes_perms)


class EvidenceDetailTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]
    url = reverse(
        "evidence-detail",
        kwargs={"curation_slug": "C000001", "evidence_slug": "E000001"},
    )
    template = "evidence/detail.html"
    page_name = "E000001 Details"
    expected_text = [
        "Data",
        "Scoring Matrix",
        "A*01:02:03",
        "acute oran berry intoxication",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    def test_shows_data_tab_content(self):
        response = self.client.get(f"{self.url}?tab=data")
        self.assertContains(response, "Genome-Wide Association Study")

    def test_shows_score_tab_content(self):
        response = self.client.get(f"{self.url}?tab=matrix")
        self.assertContains(response, "Step")
        self.assertContains(response, "Category")
        self.assertContains(response, "Points")

    def test_shows_total_score_before_multipliers(self):
        response = self.client.get(f"{self.url}?tab=matrix")
        self.assertContains(response, "Total Before Multipliers")

    def test_shows_total_score(self):
        response = self.client.get(f"{self.url}?tab=matrix")
        self.assertContains(response, "Total")


class EvidenceEditTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]
    url = reverse(
        "evidence-edit",
        kwargs={"curation_slug": "C000001", "evidence_slug": "E000001"},
    )
    template = "evidence/edit.html"
    page_name = "Edit Evidence"
    expected_text: list[str] = []  # We test this later.

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)

    # We skip this because we test it in other test methods.
    def test_expected_text_in_response(self):
        pass

    def test_marks_public_fields(self):
        html = self.client.get(self.url).content.decode()
        self.assertNotIn("public-badge", field_block(html, "id_p_value_notes"))
        self.assertIn("public-badge", field_block(html, "id_odds_ratio_string"))

    def test_badges_public_sections_in_their_headings(self):
        html = self.client.get(self.url).content.decode()

        def heading(section_id: str) -> str:
            start = html.index(f'id="{section_id}"')
            return html[start : html.index("</h2>", start)]

        self.assertIn("public-badge", heading("p-value"))
        self.assertIn("public-badge", heading("gwas"))
        self.assertIn("public-badge", heading("effect-size"))
        self.assertNotIn("public-badge", heading("needs-review"))

    def test_hidden_label_fields_have_no_badge_of_their_own(self):
        html = self.client.get(self.url).content.decode()
        self.assertNotIn("public-badge", field_block(html, "id_p_value_string"))
        self.assertNotIn("public-badge", field_block(html, "id_is_gwas"))

    def test_shows_menu(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Menu")

    def test_shows_data_headings(self):
        response = self.client.get(self.url)
        headings = [
            "GWAS",
            "Zygosity",
            "Phase",
            "Typing Method",
            "Demographics",
            "p-value",
            "Multiple Testing Correction",
            "Effect Size",
            "Confidence Interval",
            "Cohort Size",
            "Significant Association",
            "Protective",
            "Needs Review",
            "Save",
        ]
        for heading in headings:
            self.assertContains(response, heading)

    def test_edits_evidence_with_valid_form_data(self):
        data = {
            "is_gwas": True,
            "is_gwas_notes": "",
            "num_fields": 3,
            "num_fields_notes": "",
            "zygosity": Zygosity.BIALLELIC,
            "zygosity_notes": "",
            "phase_confirmed": True,
            "phase_confirmed_notes": "",
            "typing_method": TypingMethod.LONG_READ_SEQ,
            "typing_method_notes": "",
            "demographics": Demographic.objects.all(),
            "demographics_notes": "",
            "p_value_string": "1e-15",
            "p_value_notes": "",
            "multiple_testing_correction": MultipleTestingCorrection.TWO_STEP,
            "multiple_testing_correction_notes": "",
            "effect_size_statistic": EffectSizeStatistic.ODDS_RATIO,
            "effect_size_statistic_notes": "",
            "odds_ratio_string": "3.1",
            "relative_risk_string": "",
            "beta_string": "",
            "ci_start_string": "2.8",
            "ci_end_string": "3.5",
            "ci_notes": "",
            "cohort_size": 11111,
            "cohort_size_notes": "",
            "additional_phenotypes": AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED,
            "additional_phenotypes_notes": "",
            "has_association": True,
            "has_association_notes": "",
            "is_protective": False,
            "is_protective_notes": "",
            "needs_review": False,
            "needs_review_notes": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        evidence = Evidence.objects.get(pk=1)
        self.assertEqual(evidence.score, 20.0)

    @staticmethod
    def _base_evidence_data() -> dict:
        return {
            "is_gwas": True,
            "is_gwas_notes": "",
            "num_fields": 3,
            "num_fields_notes": "",
            "zygosity": Zygosity.BIALLELIC,
            "zygosity_notes": "",
            "phase_confirmed": True,
            "phase_confirmed_notes": "",
            "typing_method": "",
            "typing_method_notes": "",
            "demographics_text_quotes": "",
            "demographics": [],
            "demographics_notes": "",
            "p_value_string": "",
            "p_value_notes": "",
            "multiple_testing_correction": "",
            "multiple_testing_correction_notes": "",
            "effect_size_statistic": "",
            "effect_size_statistic_notes": "",
            "odds_ratio_string": "",
            "relative_risk_string": "",
            "beta_string": "",
            "ci_start_string": "",
            "ci_end_string": "",
            "ci_notes": "",
            "cohort_size": "",
            "cohort_size_notes": "",
            "additional_phenotypes": "",
            "additional_phenotypes_notes": "",
            "has_association": False,
            "has_association_notes": "",
            "is_protective": False,
            "is_protective_notes": "",
            "needs_review": False,
            "needs_review_notes": "",
        }

    def test_requires_text_quotes_when_demographics_provided(self):
        demographic = Demographic.objects.create(group="Asian")
        data = self._base_evidence_data()
        data["demographics"] = [demographic.pk]
        data["demographics_text_quotes"] = ""
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "demographics_text_quotes",
            "Text quotes must be provided when demographics are entered.",
        )

    def test_saves_demographics_text_quotes(self):
        demographic = Demographic.objects.create(group="Asian")
        data = self._base_evidence_data()
        data["demographics"] = [demographic.pk]
        data["demographics_text_quotes"] = "Patients were predominantly Asian (n=1500)."
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        evidence = Evidence.objects.get(pk=1)
        self.assertEqual(
            evidence.demographics_text_quotes,
            "Patients were predominantly Asian (n=1500).",
        )


def _make_user_with_profile(
    *, username: str, phi: bool = True, curate: bool = True, review: bool = False
) -> User:
    user = User.objects.create_user(username=username, password="pw")  # ruff: ignore[hardcoded-password-func-arg]
    UserProfile.objects.create(
        user=user,
        has_signed_phi_agreement=phi,
        has_curation_permissions=curate,
        has_review_permissions=review,
    )
    return user


def _make_curation(
    allele: Allele, disease: Disease, status: str = Status.IN_PROGRESS
) -> Curation:
    return Curation.objects.create(
        curation_type=CurationTypes.ALLELE,
        allele=allele,
        disease=disease,
        status=status,
    )


class CurationSubmitTest(SuppressRequestLoggingMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "demographics.json",
    ]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = _make_user_with_profile(username="curator_s")
        self.client.force_login(self.user)
        self.curation = _make_curation(self.allele, self.disease)

    def _url(self) -> str:
        return reverse("curation-submit", kwargs={"curation_slug": self.curation.slug})

    def test_submit_moves_status_to_provisional(self):
        pub = Publication.objects.get(pk=1)
        Evidence.objects.create(
            curation=self.curation,
            publication=pub,
            is_included=True,
            status=Status.DONE,
            needs_review=False,
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_submit_fails_when_no_included_evidence(self):
        pub = Publication.objects.get(pk=1)
        Evidence.objects.create(
            curation=self.curation,
            publication=pub,
            is_included=False,
            status=Status.DONE,
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)

    def test_submit_fails_when_included_evidence_not_done(self):
        pub = Publication.objects.get(pk=1)
        Evidence.objects.create(
            curation=self.curation,
            publication=pub,
            is_included=True,
            status=Status.IN_PROGRESS,
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)

    def test_submit_fails_when_included_evidence_needs_review(self):
        pub = Publication.objects.get(pk=1)
        Evidence.objects.create(
            curation=self.curation,
            publication=pub,
            is_included=True,
            status=Status.DONE,
            needs_review=True,
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)

    def test_submit_fails_when_not_in_progress(self):
        self.curation.status = Status.PROVISIONAL
        self.curation.save()
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_non_curator_gets_403(self):
        anon = User.objects.create_user(username="anon_s", password="pw")  # ruff: ignore[hardcoded-password-func-arg]
        self.client.force_login(anon)
        with self.suppress_request_logging():
            response = self.client.post(self._url())
        self.assertEqual(response.status_code, 403)


class CurationReviewTest(SuppressRequestLoggingMixin, TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json", "demographics.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.reviewer = _make_user_with_profile(username="reviewer_r", review=True)
        self.curator = _make_user_with_profile(username="curator_r")
        self.curation = _make_curation(
            self.allele, self.disease, status=Status.PROVISIONAL
        )

    def _url(self) -> str:
        return reverse("curation-review", kwargs={"curation_slug": self.curation.slug})

    @staticmethod
    def _approval_data() -> dict[str, str]:
        today = timezone.now().date()
        return {
            "decision": "approved",
            "taskforce_classification": Classification.MODERATE,
            "taskforce_evidence_summary": f"Approved on {today.isoformat()}.",
            "taskforce_additional_notes": "",
            "taskforce": HLA_CURATION_TASKFORCE_ID,
            "taskforce_review_date": timezone.now().date().isoformat(),
            # The score is 0, so no classification is suggested and any is an override.
            "taskforce_override_reason": "Taskforce judgment.",
        }

    def test_form_names_the_suggested_classification_override_reason(self):
        self.client.force_login(self.reviewer)
        response = self.client.get(self._url())
        self.assertContains(response, "Suggested Classification Override Reason")
        # History diffs label fields with their verbose_name.
        field = Curation._meta.get_field("taskforce_override_reason")  # ruff: ignore[private-member-access]
        self.assertEqual(
            getattr(field, "verbose_name", None),
            "Suggested Classification Override Reason",
        )

    def test_approval_sets_status_to_approved(self):
        self.client.force_login(self.reviewer)
        response = self.client.post(self._url(), self._approval_data())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.APPROVED)
        self.assertEqual(
            self.curation.taskforce_classification, Classification.MODERATE
        )

    def test_needs_revision_saves_reviewer_notes(self):
        self.client.force_login(self.reviewer)
        response = self.client.post(
            self._url(),
            {
                "decision": "needs_revision",
                "taskforce_evidence_summary": "Insufficient cohort size.",
                "taskforce_additional_notes": "Please address the power calculation.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)
        self.assertEqual(
            self.curation.taskforce_evidence_summary, "Insufficient cohort size."
        )
        self.assertEqual(
            self.curation.taskforce_additional_notes,
            "Please address the power calculation.",
        )
        self.assertIsNone(self.curation.taskforce_review_date)

    def test_approval_saves_review_date(self):
        self.client.force_login(self.reviewer)
        self.client.post(self._url(), self._approval_data())
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.taskforce_review_date, timezone.now().date())

    def test_approval_without_review_date_fails(self):
        self.client.force_login(self.reviewer)
        data = {**self._approval_data(), "taskforce_review_date": ""}
        response = self.client.post(self._url(), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Required when approving.")
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_future_review_date_fails(self):
        self.client.force_login(self.reviewer)
        tomorrow = (timezone.now().date() + timedelta(days=1)).isoformat()
        for decision in ("approved", "needs_revision"):
            data = {
                **self._approval_data(),
                "decision": decision,
                "taskforce_review_date": tomorrow,
            }
            response = self.client.post(self._url(), data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "can&#x27;t be in the future")
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_review_page_marks_public_fields(self):
        self.client.force_login(self.reviewer)
        html = self.client.get(self._url()).content.decode()
        self.assertIn(
            "public-badge", field_block(html, "id_taskforce_evidence_summary")
        )
        self.assertIn(
            "public-badge", field_block(html, "id_taskforce_additional_notes")
        )
        self.assertNotIn("public-badge", field_block(html, "id_decision"))

    def test_review_page_shows_earlier_feedback(self):
        self.curation.taskforce_additional_notes = "Check the cohort sizes."
        self.curation.save()
        self.client.force_login(self.reviewer)
        response = self.client.get(self._url())
        self.assertContains(response, "Check the cohort sizes.")
        self.assertContains(response, "Earlier Taskforce Feedback")

    def test_review_form_prefills_evidence_summary_template(self):
        self.client.force_login(self.reviewer)
        form = self.client.get(self._url()).context["form"]
        self.assertEqual(
            form.initial["taskforce_evidence_summary"],
            build_evidence_summary(self.curation),
        )

    def test_review_form_keeps_saved_evidence_summary(self):
        self.curation.taskforce_evidence_summary = "Consistent association."
        self.curation.save()
        self.client.force_login(self.reviewer)
        form = self.client.get(self._url()).context["form"]
        self.assertEqual(
            form.initial["taskforce_evidence_summary"], "Consistent association."
        )

    def test_approval_with_unchanged_template_fails(self):
        self.client.force_login(self.reviewer)
        # Browsers submit textarea line breaks as CRLF.
        summary = build_evidence_summary(self.curation).replace("\n", "\r\n")
        data = {**self._approval_data(), "taskforce_evidence_summary": summary}
        response = self.client.post(self._url(), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fill in the template before approving.")
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_approval_with_summary_missing_review_date_fails(self):
        self.client.force_login(self.reviewer)
        yesterday = timezone.now().date() - timedelta(days=1)
        for summary in (
            "Taskforce consensus.",
            f"Approved on {yesterday.isoformat()}.",
        ):
            data = {**self._approval_data(), "taskforce_evidence_summary": summary}
            response = self.client.post(self._url(), data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Include the review date")
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_approval_accepts_common_review_date_formats(self):
        self.client.force_login(self.reviewer)
        for spelling in (
            "September 1, 2026",
            "september  1 2026",
            "1 September 2026",
            "Sep. 1, 2026",
            "2026-09-01",
            "9/1/2026",
            "09/01/2026",
        ):
            with self.subTest(spelling=spelling):
                self.curation.status = Status.PROVISIONAL
                self.curation.save()
                data = {
                    **self._approval_data(),
                    "taskforce_review_date": "2026-09-01",
                    "taskforce_evidence_summary": f"Approved on {spelling}.",
                }
                response = self.client.post(self._url(), data)
                self.assertEqual(response.status_code, 302)

    def test_approval_rejects_review_date_inside_another_date(self):
        self.client.force_login(self.reviewer)
        data = {
            **self._approval_data(),
            "taskforce_review_date": "2026-09-01",
            "taskforce_evidence_summary": "Approved on 19/1/2026 and 2026-09-011.",
        }
        response = self.client.post(self._url(), data)
        self.assertContains(response, "Include the review date")

    def test_needs_revision_discards_unchanged_template(self):
        self.client.force_login(self.reviewer)
        data = {
            "decision": "needs_revision",
            "taskforce_evidence_summary": build_evidence_summary(self.curation),
        }
        response = self.client.post(self._url(), data)
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertIsNone(self.curation.taskforce_evidence_summary)

    def test_review_form_prefills_review_date(self):
        self.curation.taskforce_review_date = date(2026, 9, 1)
        self.curation.save()
        self.client.force_login(self.reviewer)
        response = self.client.get(self._url())
        self.assertContains(response, 'value="2026-09-01"')

    def test_non_taskforce_user_gets_403(self):
        self.client.force_login(self.curator)
        with self.suppress_request_logging():
            response = self.client.post(self._url(), self._approval_data())
        self.assertEqual(response.status_code, 403)

    def _post_with_score(self, data: dict[str, str], score: float) -> HttpResponseBase:
        self.client.force_login(self.reviewer)
        with patch.object(
            Curation, "score", new_callable=PropertyMock, return_value=score
        ):
            return self.client.post(self._url(), data)

    def test_matching_suggestion_needs_no_override_reason(self):
        data = {
            **self._approval_data(),
            "taskforce_classification": Classification.LIMITED,
        }
        response = self._post_with_score(data, 10)
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.APPROVED)

    def test_override_without_reason_fails(self):
        data = {**self._approval_data(), "taskforce_override_reason": ""}
        response = self._post_with_score(data, 10)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Explain why the taskforce chose")
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)

    def test_override_with_reason_saves_both(self):
        data = {
            **self._approval_data(),
            "taskforce_override_reason": "Replicated twice.",
        }
        response = self._post_with_score(data, 10)
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(
            self.curation.taskforce_classification, Classification.MODERATE
        )
        self.assertEqual(self.curation.taskforce_override_reason, "Replicated twice.")

    def test_approving_without_override_clears_old_reason(self):
        self.curation.taskforce_override_reason = "From an earlier review."
        self.curation.save()
        data = {
            **self._approval_data(),
            "taskforce_classification": Classification.LIMITED,
            "taskforce_override_reason": "From an earlier review.",
        }
        self._post_with_score(data, 10)
        self.curation.refresh_from_db()
        self.assertIsNone(self.curation.taskforce_override_reason)

    def test_review_form_preselects_suggestion_and_labels_it(self):
        self.client.force_login(self.reviewer)
        with patch.object(
            Curation, "score", new_callable=PropertyMock, return_value=10
        ):
            response = self.client.get(self._url())
        self.assertContains(response, "Classification (suggested: Limited)")
        self.assertContains(response, '<option value="LIM" selected>')
        self.assertNotContains(response, "confirm(")


class CurationCopyTest(SuppressRequestLoggingMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "demographics.json",
    ]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = _make_user_with_profile(username="curator_f")
        self.client.force_login(self.user)
        self.curation = _make_curation(
            self.allele, self.disease, status=Status.PUBLISHED
        )
        self.published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )

    def _url(self) -> str:
        return reverse("curation-copy", kwargs={"curation_slug": self.curation.slug})

    def test_copy_creates_new_curation_with_copied_from_set(self):
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        copy = Curation.objects.exclude(pk=self.curation.pk).first()
        assert copy is not None
        self.assertEqual(copy.copied_from, self.curation)
        self.assertEqual(copy.status, Status.IN_PROGRESS)

    def test_copy_deep_copies_evidence(self):
        pub = Publication.objects.get(pk=1)
        Evidence.objects.create(
            curation=self.curation, publication=pub, is_included=True
        )
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        copy = Curation.objects.exclude(pk=self.curation.pk).first()
        assert copy is not None
        self.assertEqual(copy.evidence.count(), 1)  # type: ignore

    def test_copy_succeeds_when_two_root_curations_exist(self):
        _make_curation(self.allele, self.disease)
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Curation.objects.filter(copied_from=self.curation).exists())

    def test_copy_fails_when_source_not_published(self):
        curation2 = _make_curation(self.allele, self.disease)
        url = reverse("curation-copy", kwargs={"curation_slug": curation2.slug})
        with self.suppress_request_logging():
            response = self.client.post(url)
        self.assertEqual(response.status_code, 400)


class LockingTest(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "demographics.json",
    ]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = _make_user_with_profile(username="curator_l")
        self.client.force_login(self.user)

    def _assert_locked(self, curation: Curation, expected_redirect: str) -> None:
        ev_edit_url = reverse(
            "curation-edit-evidence", kwargs={"curation_slug": curation.slug}
        )
        response = self.client.get(ev_edit_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_redirect)

    def test_provisional_locks_evidence_edit(self):
        curation = _make_curation(self.allele, self.disease, status=Status.PROVISIONAL)
        self._assert_locked(
            curation,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )

    def test_approved_locks_evidence_edit(self):
        curation = _make_curation(self.allele, self.disease, status=Status.APPROVED)
        self._assert_locked(
            curation,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )

    def test_provisional_locks_evidence_create(self):
        curation = _make_curation(self.allele, self.disease, status=Status.PROVISIONAL)
        url = reverse("evidence-create", kwargs={"curation_slug": curation.slug})
        response = self.client.post(url, {"publication": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evidence.objects.filter(curation=curation).count(), 0)

    def test_published_locks_evidence_edit(self):
        curation = _make_curation(self.allele, self.disease, status=Status.PUBLISHED)
        self._assert_locked(
            curation,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )


class CurationPublishUpdatedTest(TestCase):
    """Verify publish now requires APPROVED status, not DONE."""

    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = _make_user_with_profile(username="curator_p")
        self.client.force_login(self.user)

    def test_publish_requires_approved_status(self):
        curation = _make_curation(self.allele, self.disease, status=Status.IN_PROGRESS)
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 0)

    def test_publish_succeeds_with_approved_status(self):
        curation = _make_curation(self.allele, self.disease, status=Status.APPROVED)
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 1)
        curation.refresh_from_db()
        self.assertEqual(curation.status, Status.PUBLISHED)

    def test_get_does_not_publish(self):
        curation = _make_curation(self.allele, self.disease, status=Status.APPROVED)
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )
        self.assertEqual(PublishedCuration.objects.count(), 0)
        curation.refresh_from_db()
        self.assertEqual(curation.status, Status.APPROVED)

    def test_detail_buttons_use_the_confirm_modal(self):
        for status in (Status.IN_PROGRESS, Status.APPROVED):
            with self.subTest(status=status):
                curation = _make_curation(self.allele, self.disease, status=status)
                url = reverse(
                    "curation-detail", kwargs={"curation_slug": curation.slug}
                )
                response = self.client.get(url)
                self.assertContains(response, "data-confirm=")
                self.assertContains(response, 'id="confirm-modal"')
                self.assertNotContains(response, "confirm(")
