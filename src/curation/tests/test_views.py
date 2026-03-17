"""Houses tests for the curation app's views."""

from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import ProtectedViewTestMixin
from curation.constants.models.common import Status
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
        self.assertIsNotNone(new_curation)
        self.assertEqual(new_curation.curation_type, "ALL")  # type: ignore[union-attr]
        self.assertEqual(new_curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.disease, Disease.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_curation.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]

    def test_creates_haplotype_curation_with_valid_form_data(self):
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
        self.assertEqual(new_curation.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]


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
        "Limited",
        "1970-01-01",
        "ID",
        "Publication",
        "Needs Review",
        "Status",
        "Conflicting",
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
        self.assertContains(response, "2.0")


class CurationEditTest(ProtectedViewTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]
    url = reverse("curation-edit", kwargs={"curation_slug": "C000001"})
    template = "curation/edit/curation.html"
    page_name = "Edit Curation"
    expected_text = [
        "Edit Curation",
        "Status",
        "Classification",
        "Save",
        "Cancel",
    ]

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user4_yes_phi_yes_perms)


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
        "Conflicting",
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
        "Added",
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
        self.assertIsNotNone(new_evidence)
        self.assertEqual(new_evidence.curation.allele, Allele.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_evidence.curation.disease, Disease.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertEqual(new_evidence.publication, Publication.objects.get(pk=1))  # type: ignore[union-attr]
        self.assertFalse(new_evidence.needs_review)  # type: ignore[union-attr]
        self.assertEqual(new_evidence.status, Status.IN_PROGRESS)  # type: ignore[union-attr]
        self.assertEqual(new_evidence.added_by, self.user4_yes_phi_yes_perms)  # type: ignore[union-attr]


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
