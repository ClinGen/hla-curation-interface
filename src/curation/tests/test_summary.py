"""Houses tests for the curation app's evidence summary builder."""

from unittest.mock import PropertyMock, patch

from django.test import TestCase

from allele.models import Allele
from curation.constants.models.curation import (
    CLASSIFICATION_CHOICES,
    Classification,
    CurationTypes,
)
from curation.constants.models.evidence import NumFields, Zygosity
from curation.models import Curation, Evidence
from curation.summary import build_evidence_summary
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication


def _is_balanced(text: str) -> bool:
    pairs = {")": "(", "]": "["}
    stack = []
    for char in text:
        if char in "([":
            stack.append(char)
        elif char in ")]" and (not stack or stack.pop() != pairs[char]):
            return False
    return not stack


class BuildEvidenceSummaryTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json", "test_haplotypes.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
        )
        self.pair = f"{self.allele.display_name}\N{EN DASH}{self.disease.name}"

    def _add_evidence(self, pubmed_id: str, year: int = 2020, **fields) -> Evidence:
        publication, _ = Publication.objects.get_or_create(
            pubmed_id=pubmed_id,
            defaults={"slug": f"P{pubmed_id}", "publication_year": year},
        )
        defaults = {
            "is_included": True,
            "num_fields": NumFields.TWO,
            "has_association": True,
        }
        return Evidence.objects.create(
            curation=self.curation, publication=publication, **(defaults | fields)
        )

    def _summary(self, score: float = 10) -> str:
        with patch.object(
            Curation, "score", new_callable=PropertyMock, return_value=score
        ):
            return build_evidence_summary(self.curation)

    def test_fills_names_and_mondo_id(self):
        self._add_evidence("111")
        summary = self._summary()
        self.assertTrue(summary.startswith(f"{self.pair} Curation Summary\n\n"))
        self.assertIn(
            f"{self.disease.name[0].upper()}{self.disease.name[1:]} "
            f"({self.disease.mondo_id}) is characterized by",
            summary,
        )
        self.assertIn(f"mapped to {self.disease.mondo_id}.", summary)

    def test_leaves_first_report_bracketed(self):
        self._add_evidence("111")
        self.assertIn(
            f"{self.allele.display_name} was first reported in association with "
            f"{self.disease.name} by [Author] et al. [year] (PMID: [ ]).",
            self._summary(),
        )

    def test_brackets_are_balanced(self):
        self._add_evidence("111", num_fields=None, has_association=False)
        self.assertTrue(_is_balanced(self._summary()))

    def test_single_publication(self):
        self._add_evidence("111")
        summary = self._summary()
        self.assertIn("evidence from 1 publication (PMID: 111).", summary)
        self.assertIn("This was identified", summary)
        self.assertIn("The evidence comprises 1 case-control study.", summary)

    def test_lists_distinct_publications_by_year(self):
        self._add_evidence("222", year=2021, is_gwas=True)
        self._add_evidence("111", year=2019)
        self._add_evidence("222", year=2021)
        summary = self._summary()
        self.assertIn("evidence from 2 publications (PMIDs: 111, 222).", summary)
        self.assertIn("These were identified", summary)
        self.assertIn(
            "comprises 1 genome-wide association study (GWAS) and 2 case-control "
            "studies.",
            summary,
        )

    def test_excludes_evidence_that_is_not_included(self):
        self._add_evidence("111")
        self._add_evidence("222", is_included=False)
        self.assertIn("(PMID: 111).", self._summary())

    def test_zygosity_all_monoallelic(self):
        self._add_evidence("111")
        self.assertIn(
            "The allele was heterozygous (monoallelic) in all studies.",
            self._summary(),
        )

    def test_zygosity_some_biallelic(self):
        self._add_evidence("111")
        self._add_evidence("222", zygosity=Zygosity.BIALLELIC)
        self._add_evidence("333")
        self.assertIn(
            "heterozygous (monoallelic) in 2/3 of the scored evidence and homozygous "
            "in 1.",
            self._summary(),
        )

    def test_resolution_all_two_field(self):
        self._add_evidence("111")
        self.assertIn("All evidence was typed at 2-field resolution. ", self._summary())

    def test_resolution_with_higher_fields(self):
        self._add_evidence("111")
        self._add_evidence("222", num_fields=NumFields.THREE)
        self._add_evidence("333", num_fields=NumFields.FOUR)
        self.assertIn(
            "All evidence was typed at 2-field resolution, except for 2 studies where "
            "the genotyping method allowed 3-field or 4-field resolution.",
            self._summary(),
        )

    def test_resolution_unknown_stays_bracketed(self):
        self._add_evidence("111", num_fields=None)
        self.assertIn(
            "[, except for [n] studies where the genotyping method allowed 3-field "
            "[4-field] resolution].",
            self._summary(),
        )

    def test_all_associations_significant(self):
        self._add_evidence("111")
        self._add_evidence("222")
        summary = self._summary()
        self.assertIn(
            "All scored associations were statistically significant.", summary
        )
        self.assertNotIn("reasons for disagreement", summary)

    def test_some_associations_not_significant(self):
        self._add_evidence("111")
        self._add_evidence("222", has_association=False)
        summary = self._summary()
        self.assertIn(
            "1 of 2 scored associations were statistically significant. [Briefly "
            "discuss potential reasons for disagreement.]",
            summary,
        )

    def test_single_association_not_significant(self):
        self._add_evidence("111", has_association=False)
        self.assertIn(
            "The scored association was not statistically significant.",
            self._summary(),
        )

    def test_total_score(self):
        self._add_evidence("111")
        self.assertIn(
            f"The total score for the {self.pair} pair is 12.5 points.",
            self._summary(score=12.5),
        )

    def test_uses_suggested_classification(self):
        self._add_evidence("111")
        # A score of 10 suggests Limited.
        label = CLASSIFICATION_CHOICES[Classification.LIMITED].lower()
        self.assertIn(f"there is {label} evidence supporting", self._summary())

    def test_prefers_taskforce_classification(self):
        self._add_evidence("111")
        self.curation.taskforce_classification = Classification.MODERATE
        label = CLASSIFICATION_CHOICES[Classification.MODERATE].lower()
        self.assertIn(f"there is {label} evidence supporting", self._summary())

    def test_classification_that_is_not_an_evidence_level_stays_bracketed(self):
        self._add_evidence("111")
        self.curation.taskforce_classification = Classification.DISPUTED
        self.assertIn("there is [classification] evidence", self._summary())

    def test_haplotype_wording(self):
        haplotype = Haplotype.objects.get(pk=1)
        self.curation.curation_type = CurationTypes.HAPLOTYPE
        self.curation.allele = None
        self.curation.haplotype = haplotype
        self.curation.save()
        self._add_evidence("111")
        summary = self._summary()
        self.assertTrue(summary.startswith(haplotype.display_name))
        self.assertIn("[Discuss the haplotype structure.]", summary)
        self.assertIn("The haplotype was heterozygous", summary)

    def test_allele_omits_haplotype_structure(self):
        self._add_evidence("111")
        self.assertNotIn("haplotype structure", self._summary())

    def test_no_included_evidence_stays_bracketed(self):
        self.assertIn(
            "evidence from [n] publications (PMIDs: [ ]).", self._summary(score=0)
        )
