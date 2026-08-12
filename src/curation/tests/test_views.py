"""Houses tests for the curation app's views."""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from auth_.models import UserProfile
from common.tests import ProtectedViewTestMixin, SuppressRequestLoggingMixin
from curation.constants.models.common import Status
from curation.constants.models.curation import Classification, CurationTypes
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
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication
from repo.models import PublishedCuration


class CurationCreateTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json", "test_diseases.json"]
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
        "1970-01-01",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


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
    user = User.objects.create_user(username=username, password="pw")  # noqa: S106
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

    def test_submit_moves_status_to_ready_for_review(self):
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
        self.assertEqual(self.curation.status, Status.READY_FOR_REVIEW)

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
        self.curation.status = Status.READY_FOR_REVIEW
        self.curation.save()
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.READY_FOR_REVIEW)

    def test_non_curator_gets_403(self):
        anon = User.objects.create_user(username="anon_s", password="pw")  # noqa: S106
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
            self.allele, self.disease, status=Status.READY_FOR_REVIEW
        )

    def _url(self) -> str:
        return reverse("curation-review", kwargs={"curation_slug": self.curation.slug})

    @staticmethod
    def _approval_data() -> dict[str, str]:
        return {
            "decision": "approved",
            "ep_classification": Classification.MODERATE,
            "ep_evidence_summary": "Panel consensus.",
            "ep_additional_notes": "",
            "ep": "40033",
        }

    def test_approval_sets_status_to_provisional(self):
        self.client.force_login(self.reviewer)
        response = self.client.post(self._url(), self._approval_data())
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PROVISIONAL)
        self.assertEqual(self.curation.ep_classification, Classification.MODERATE)

    def test_needs_revision_saves_reviewer_notes(self):
        self.client.force_login(self.reviewer)
        response = self.client.post(
            self._url(),
            {
                "decision": "needs_revision",
                "ep_evidence_summary": "Insufficient cohort size.",
                "ep_additional_notes": "Please address the power calculation.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)
        self.assertEqual(self.curation.ep_evidence_summary, "Insufficient cohort size.")
        self.assertEqual(
            self.curation.ep_additional_notes, "Please address the power calculation."
        )

    def test_non_ep_user_gets_403(self):
        self.client.force_login(self.curator)
        with self.suppress_request_logging():
            response = self.client.post(self._url(), self._approval_data())
        self.assertEqual(response.status_code, 403)


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

    def test_ready_for_review_locks_evidence_edit(self):
        curation = _make_curation(
            self.allele, self.disease, status=Status.READY_FOR_REVIEW
        )
        self._assert_locked(
            curation,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )

    def test_provisional_locks_evidence_edit(self):
        curation = _make_curation(self.allele, self.disease, status=Status.PROVISIONAL)
        self._assert_locked(
            curation,
            reverse("curation-detail", kwargs={"curation_slug": curation.slug}),
        )

    def test_ready_for_review_locks_evidence_create(self):
        curation = _make_curation(
            self.allele, self.disease, status=Status.READY_FOR_REVIEW
        )
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
    """Verify publish now requires PROVISIONAL status, not DONE."""

    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = _make_user_with_profile(username="curator_p")
        self.client.force_login(self.user)

    def test_publish_requires_provisional_status(self):
        curation = _make_curation(self.allele, self.disease, status=Status.IN_PROGRESS)
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 0)

    def test_publish_succeeds_with_provisional_status(self):
        curation = _make_curation(self.allele, self.disease, status=Status.PROVISIONAL)
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 1)
        curation.refresh_from_db()
        self.assertEqual(curation.status, Status.PUBLISHED)
