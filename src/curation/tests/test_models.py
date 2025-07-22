"""Houses tests for the curation app's models."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from allele.models import Allele
from curation.models import (
    AdditionalPhenotypes,
    Classification,
    Curation,
    CurationTypes,
    Demographic,
    EffectSizeStatistic,
    Evidence,
    MultipleTestingCorrection,
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

    def test_can_add_p_value(self):
        p_value_string = "1e-13"
        self.evidence.p_value = Decimal(p_value_string)
        self.evidence.save()
        self.assertIsNotNone(self.evidence.p_value)

    def test_score_increases_when_p_value_provided(self):
        initial_points = self.evidence.score
        p_value_string = "0.0004"
        self.evidence.p_value = Decimal(p_value_string)
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3A_INTERVAL_4)

    def test_multiple_testing_correction_is_empty_when_created(self):
        self.assertEqual(self.evidence.multiple_testing_correction, "")

    def test_score_increases_when_multiple_testing_correction_overall_selected(self):
        initial_points = self.evidence.score
        self.evidence.multiple_testing_correction = MultipleTestingCorrection.OVERALL
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3B_OVERALL)

    def test_score_increases_when_multiple_testing_correction_two_step_selected(self):
        initial_points = self.evidence.score
        self.evidence.multiple_testing_correction = MultipleTestingCorrection.TWO_STEP
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3B_TWO_STEP)

    def test_effect_size_statistic_is_empty_when_created(self):
        self.assertEqual(self.evidence.effect_size_statistic, "")

    def test_odds_ratio_is_none_when_created(self):
        self.assertIsNone(self.evidence.odds_ratio)

    def test_can_add_odds_ratio(self):
        odds_ratio_value = Decimal("2.5")
        self.evidence.odds_ratio = odds_ratio_value
        self.evidence.save()
        self.assertEqual(self.evidence.odds_ratio, odds_ratio_value)

    def test_score_increases_when_odds_ratio_provided_high(self):
        initial_points = self.evidence.score
        self.evidence.odds_ratio = Decimal("2.5")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_score_increases_when_odds_ratio_provided_low(self):
        initial_points = self.evidence.score
        self.evidence.odds_ratio = Decimal("0.4")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_relative_risk_is_none_when_created(self):
        self.assertIsNone(self.evidence.relative_risk)

    def test_can_add_relative_risk(self):
        relative_risk_value = Decimal("1.8")
        self.evidence.relative_risk = relative_risk_value
        self.evidence.save()
        self.assertEqual(self.evidence.relative_risk, relative_risk_value)

    def test_score_increases_when_relative_risk_provided_high(self):
        initial_points = self.evidence.score
        self.evidence.relative_risk = Decimal("2.1")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_score_increases_when_relative_risk_provided_low(self):
        initial_points = self.evidence.score
        self.evidence.relative_risk = Decimal("0.3")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_beta_is_none_when_created(self):
        self.assertIsNone(self.evidence.beta)

    def test_can_add_beta(self):
        beta_value = Decimal("0.8")
        self.evidence.beta = beta_value
        self.evidence.save()
        self.assertEqual(self.evidence.beta, beta_value)

    def test_score_increases_when_beta_provided_high(self):
        initial_points = self.evidence.score
        self.evidence.beta = Decimal("0.6")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_score_increases_when_beta_provided_low(self):
        initial_points = self.evidence.score
        self.evidence.beta = Decimal("-0.7")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S3C_OR_RR_BETA)

    def test_ci_start_is_none_when_created(self):
        self.assertIsNone(self.evidence.ci_start)

    def test_ci_end_is_none_when_created(self):
        self.assertIsNone(self.evidence.ci_end)

    def test_can_add_confidence_interval(self):
        ci_start_value = Decimal("1.2")
        ci_end_value = Decimal("3.8")
        self.evidence.ci_start = ci_start_value
        self.evidence.ci_end = ci_end_value
        self.evidence.save()
        self.assertEqual(self.evidence.ci_start, ci_start_value)
        self.assertEqual(self.evidence.ci_end, ci_end_value)

    def test_score_increases_when_ci_does_not_cross_one_for_odds_ratio(self):
        initial_points = self.evidence.score
        self.evidence.effect_size_statistic = EffectSizeStatistic.ODDS_RATIO
        self.evidence.ci_start = Decimal("1.2")
        self.evidence.ci_end = Decimal("3.8")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(
            self.evidence.score, initial_points + Points.S3C_CI_DOES_NOT_CROSS
        )

    def test_score_increases_when_ci_does_not_cross_zero_for_beta(self):
        initial_points = self.evidence.score
        self.evidence.effect_size_statistic = EffectSizeStatistic.BETA
        self.evidence.ci_start = Decimal("0.2")
        self.evidence.ci_end = Decimal("0.8")
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(
            self.evidence.score, initial_points + Points.S3C_CI_DOES_NOT_CROSS
        )

    def test_cohort_size_is_none_when_created(self):
        self.assertIsNone(self.evidence.cohort_size)

    def test_can_add_cohort_size(self):
        cohort_size_value = 1500
        self.evidence.cohort_size = cohort_size_value
        self.evidence.save()
        self.assertEqual(self.evidence.cohort_size, cohort_size_value)

    def test_score_increases_when_cohort_size_provided_non_gwas(self):
        initial_points = self.evidence.score
        self.evidence.cohort_size = 150
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S4_INTERVAL_3)

    def test_score_increases_when_cohort_size_provided_gwas(self):
        initial_points = self.evidence.score
        self.evidence.is_gwas = True
        self.evidence.cohort_size = 3000
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(self.evidence.score, initial_points + Points.S4_INTERVAL_3)

    def test_additional_phenotypes_is_empty_when_created(self):
        self.assertEqual(self.evidence.additional_phenotypes, "")

    def test_score_increases_when_specific_disease_related_phenotype_selected(self):
        initial_points = self.evidence.score
        self.evidence.additional_phenotypes = (
            AdditionalPhenotypes.SPECIFIC_DISEASE_RELATED
        )
        self.evidence.save()
        self.assertGreater(self.evidence.score, initial_points)
        self.assertEqual(
            self.evidence.score, initial_points + Points.S5_SPECIFIC_PHENOTYPE
        )

    def test_score_does_not_increase_when_only_disease_tested_selected(self):
        initial_points = self.evidence.score
        self.evidence.additional_phenotypes = AdditionalPhenotypes.ONLY_DISEASE_TESTED
        self.evidence.save()
        self.assertEqual(
            self.evidence.score, initial_points + Points.S5_ONLY_DISEASE_TESTED
        )

    def test_has_association_is_true_when_created(self):
        self.assertTrue(self.evidence.has_association)

    def test_score_multiplied_by_zero_when_no_association(self):
        self.evidence.has_association = False
        self.evidence.save()
        self.assertEqual(self.evidence.score, 0.0)

    def test_needs_review_is_false_when_created(self):
        self.assertFalse(self.evidence.needs_review)

    def test_can_set_needs_review(self):
        self.evidence.needs_review = True
        self.evidence.save()
        self.assertTrue(self.evidence.needs_review)
