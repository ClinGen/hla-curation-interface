"""Houses tests for the curation app's models."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from allele.models import Allele
from curation.models import Classification, Curation, CurationTypes, Status
from disease.models import Disease


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
