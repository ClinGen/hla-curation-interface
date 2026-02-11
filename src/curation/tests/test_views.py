"""Houses tests for the curation app's views."""

from django.test import TestCase
from django.urls import reverse

from allele.models import Allele
from common.tests import CreateTestMixin, ViewTestMixin
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


class CurationCreateTest(CreateTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_haplotypes.json", "test_diseases.json"]

    def setUp(self):
        self.url = reverse("curation-create")
        super().setUp()

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Add Curation")

    def test_shows_radio_buttons(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Allele")
        self.assertContains(response, "Haplotype")

    def test_shows_allele_select(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Allele")

    def test_shows_disease_select(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Disease")

    def test_shows_submit_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Submit")

    def test_creates_allele_curation_with_valid_form_data(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
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
        self.client.force_login(self.user4_yes_phi_yes_perms)
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


class CurationDetailTest(ViewTestMixin, TestCase):
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

    def test_shows_evidence_in_tbody(self):
        response = self.client.get(self.url)
        self.assertContains(response, "E000001")
        self.assertContains(
            response, "Diseases in grass type Pokémon in the Kanto region"
        )
        self.assertContains(response, "2.0")


class CurationEditTest(CreateTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.url = reverse("curation-edit", kwargs={"curation_slug": "C000001"})
        super().setUp()

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Curation Search")

    def test_shows_save_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Save")

    def test_shows_cancel_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Cancel")

    def test_shows_allele(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "A*01:02:03")

    def test_shows_disease(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "acute oran berry intoxication")

    def test_shows_status(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Status")

    def test_shows_classification(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Classification")

    def test_shows_score(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Score")

    def test_shows_curation_id(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "C000001")

    def test_shows_added_at(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "1970-01-01")


class CurationEditEvidenceTest(CreateTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.url = reverse(
            "curation-edit-evidence", kwargs={"curation_slug": "C000001"}
        )
        super().setUp()

    def test_shows_breadcrumb(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Curation Search")

    def test_shows_allele_name(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "A*01:02:03")

    def test_shows_disease_name(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "acute oran berry intoxication")

    def test_shows_status(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "In Progress")

    def test_shows_classification(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Limited")

    def test_shows_score(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Score")

    def test_shows_curation_id(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "C000001")

    def test_shows_added_at(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "1970-01-01")

    def test_shows_save_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Save")

    def test_shows_cancel_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Cancel")

    def test_shows_evidence_table_headers(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "ID")
        self.assertContains(response, "Publication")
        self.assertContains(response, "Needs Review")
        self.assertContains(response, "Status")
        self.assertContains(response, "Conflicting")
        self.assertContains(response, "Included")
        self.assertContains(response, "Score")

    def test_shows_evidence_in_tbody(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "E000001")
        self.assertContains(
            response, "Diseases in grass type Pokémon in the Kanto region"
        )
        self.assertContains(response, "2.0")


class CurationListTest(ViewTestMixin, TestCase):
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


class EvidenceCreateTest(CreateTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
    ]

    def setUp(self):
        self.url = reverse("evidence-create", kwargs={"curation_slug": "C000001"})
        super().setUp()

    def test_shows_publication_input(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Publication")

    def test_shows_submit_button(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Submit")

    def test_creates_evidence_with_valid_form_data(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
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


class EvidenceDetailTest(ViewTestMixin, TestCase):
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
        "Score",
        "A*01:02:03",
        "acute oran berry intoxication",
    ]

    def test_shows_data_tab_content(self):
        response = self.client.get(f"{self.url}?tab=data")
        self.assertContains(response, "Genome-Wide Association Study")

    def test_shows_score_tab_content(self):
        response = self.client.get(f"{self.url}?tab=score")
        self.assertContains(response, "Step")
        self.assertContains(response, "Category")
        self.assertContains(response, "Points")

    def test_shows_total_score_before_multipliers(self):
        response = self.client.get(f"{self.url}?tab=score")
        self.assertContains(response, "Total Before Multipliers")

    def test_shows_total_score(self):
        response = self.client.get(f"{self.url}?tab=score")
        self.assertContains(response, "Total")


class EvidenceEditTest(CreateTestMixin, TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_publications.json",
        "test_curations.json",
        "test_evidence.json",
    ]

    def setUp(self):
        self.url = reverse(
            "evidence-edit",
            kwargs={"curation_slug": "C000001", "evidence_slug": "E000001"},
        )
        super().setUp()

    def test_shows_menu(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertContains(response, "Menu")

    def test_shows_data_headings(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
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
        self.client.force_login(self.user4_yes_phi_yes_perms)
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
