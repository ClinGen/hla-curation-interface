"""Houses tests for the curation app's models."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from allele.models import Allele
from curation.models import (
    Classification,
    Curation,
    CurationTypes,
    Demographic,
    Evidence,
    Points,
    Status,
    TypingMethod,
    Zygosity,
)
from disease.models import Disease
from publication.models import Publication


class TestCuration(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
        )

    def test_status_is_in_progress_when_created(self):
        self.assertEqual(self.curation.status, Status.IN_PROGRESS)

    def test_classification_is_no_known_when_created(self):
        self.assertEqual(self.curation.classification, Classification.NO_KNOWN)

    def test_is_not_valid_when_allele_not_provided_at_creation(self):
        with self.assertRaises(ValidationError):
            curation = Curation(
                curation_type=CurationTypes.ALLELE,
                allele=None,
                disease=self.disease,
            )
            curation.clean()

    def test_is_not_valid_when_haplotype_not_provided_at_creation(self):
        with self.assertRaises(ValidationError):
            curation = Curation(
                curation_type=CurationTypes.HAPLOTYPE,
                haplotype=None,
                disease=self.disease,
            )
            curation.clean()


class TestEvidence(TestCase):
    fixtures = [
        "test_alleles.json",
        "test_diseases.json",
        "test_curations.json",
        "test_publications.json",
        "demographics.json",
    ]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation.objects.get(pk=1)
        self.publication = Publication.objects.get(pk=1)
        self.evidence = Evidence(
            curation=self.curation,
            publication=self.publication,
        )
        self.evidence.save()

    def test_status_is_in_progress_when_created(self):
        self.assertEqual(self.evidence.status, Status.IN_PROGRESS)

    def test_conflicting_is_false_when_created(self):
        self.assertFalse(self.evidence.is_conflicting)

    def test_included_is_false_when_created(self):
        self.assertFalse(self.evidence.is_included)

    def test_gwas_is_false_when_created(self):
        self.assertFalse(self.evidence.is_gwas)

    def test_is_monoallelic_when_created(self):
        self.assertEqual(self.evidence.zygosity, Zygosity.MONOALLELIC)

    def test_score_increases_when_biallelic_selected(self):
        initial_points = self.evidence.score
        self.evidence.zygosity = Zygosity.BIALLELIC
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S1C_BIALLELIC)

    def test_phase_confirmed_is_false_when_created(self):
        self.assertFalse(self.evidence.phase_confirmed)

    def test_score_increases_when_phase_confirmed(self):
        initial_points = self.evidence.score
        self.evidence.phase_confirmed = True
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(
            self.evidence.score, initial_points + Points.S1D_PHASE_CONFIRMED
        )

    def test_typing_method_is_empty_when_created(self):
        self.assertEqual(self.evidence.typing_method, "")

    def test_score_increases_when_typing_method_selected(self):
        initial_points = self.evidence.score
        self.evidence.typing_method = TypingMethod.LONG_READ_SEQ
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S2_LONG_READ_SEQ)

    def test_demographics_is_empty_when_created(self):
        self.assertEqual(len(self.evidence.demographics.all()), 0)

    def test_can_add_demographic(self):
        demographic = Demographic.objects.get(pk=1)
        self.evidence.demographics.add(demographic)
        self.evidence.save()
        self.assertIn(demographic, self.evidence.demographics.all())

    def test_p_value_is_empty_when_created(self):
        self.assertIsNone(self.evidence.p_value)
