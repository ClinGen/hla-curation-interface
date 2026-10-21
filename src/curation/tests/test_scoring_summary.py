"""Houses tests for the curation app's scoring summary builder."""

from decimal import Decimal

from django.test import TestCase

from allele.models import Allele
from curation.constants.models.curation import CurationTypes
from curation.constants.models.evidence import NumFields, TypingMethod, Zygosity
from curation.constants.score import Intervals, Points
from curation.constants.views import FRAMEWORK
from curation.models import Curation, Evidence
from curation.scoring_summary import (
    ScoringSummary,
    SummaryCategory,
    SummaryRow,
    SummaryStep,
    build_evidence_scoring_summary,
    build_scoring_summary,
)
from disease.models import Disease
from haplotype.models import Haplotype
from publication.models import Publication
from repo.serializers import format_decimal


class BuildScoringSummaryTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json", "test_haplotypes.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
        )

    def _add_evidence(self, pubmed_id: str, **fields) -> Evidence:
        publication, _ = Publication.objects.get_or_create(
            pubmed_id=pubmed_id, defaults={"slug": f"P{pubmed_id}"}
        )
        defaults = {
            "is_included": True,
            "num_fields": NumFields.TWO,
            "has_association": True,
        }
        return Evidence.objects.create(
            curation=self.curation, publication=publication, **(defaults | fields)
        )

    @staticmethod
    def _category(summary: ScoringSummary, name: str) -> SummaryCategory:
        return next(c for c in summary.categories if c.name == name)

    @staticmethod
    def _step(summary: ScoringSummary, prefix: str) -> SummaryStep:
        steps = [s for c in summary.categories for s in c.steps]
        return next(s for s in steps if s.label.startswith(f"Step {prefix}:"))

    def _row(self, summary: ScoringSummary, prefix: str, points: float) -> SummaryRow:
        return next(r for r in self._step(summary, prefix).rows if r.points == points)

    def test_header_has_names_and_publication_count(self):
        self._add_evidence("111")
        self._add_evidence("222")
        summary = build_scoring_summary(self.curation)
        self.assertEqual(summary.subject_type, "Allele")
        self.assertEqual(summary.subject, self.allele.display_name)
        self.assertEqual(summary.car_id, self.allele.car_id)
        self.assertEqual(summary.mondo_id, self.disease.mondo_id)
        self.assertEqual(summary.disease, self.disease.name)
        self.assertEqual(summary.num_publications, 2)

    def test_counts_each_publication_once(self):
        self._add_evidence("111")
        self._add_evidence("111", is_gwas=True)
        self._add_evidence("222")
        self.assertEqual(build_scoring_summary(self.curation).num_publications, 2)

    def test_multiplier_note_lists_each_pmid_once(self):
        self._add_evidence("333", has_association=False)
        self._add_evidence("333", has_association=False, is_gwas=True)
        multipliers = self._category(
            build_scoring_summary(self.curation), "Multipliers"
        )
        self.assertTrue(multipliers.note.endswith(" in PMID: 333"))

    def test_header_uses_the_haplotype_name(self):
        haplotype = Haplotype.objects.first()
        assert haplotype is not None
        curation = Curation.objects.create(
            curation_type=CurationTypes.HAPLOTYPE,
            haplotype=haplotype,
            disease=self.disease,
        )
        summary = build_scoring_summary(curation)
        self.assertEqual(summary.subject_type, "Haplotype")
        self.assertEqual(summary.subject, haplotype.display_name)
        self.assertEqual(summary.car_id, "")

    def test_counts_gwas_and_non_gwas_studies(self):
        self._add_evidence("111", is_gwas=True)
        self._add_evidence("222")
        self._add_evidence("333")
        design = self._category(build_scoring_summary(self.curation), "Study design")
        counts = [row.count for row in design.steps[0].rows]
        self.assertEqual(counts, [1, 2])
        self.assertIsNone(design.counted)

    def test_counts_each_category_by_its_points(self):
        self._add_evidence("111", num_fields=NumFields.FOUR)
        self._add_evidence("222", num_fields=NumFields.FOUR)
        self._add_evidence("333", typing_method=TypingMethod.SANGER_SEQ)
        summary = build_scoring_summary(self.curation)
        self.assertEqual(self._row(summary, "1B", Points.S1B_4_FIELD).count, 2)
        self.assertEqual(self._row(summary, "1B", Points.S1B_2_FIELD).count, 1)
        self.assertEqual(self._row(summary, "2", Points.S2_SANGER_SEQ).count, 1)
        self.assertEqual(self._row(summary, "1A", Points.S1A_ALLELE).count, 3)

    def test_step_total_sums_points_before_multipliers(self):
        self._add_evidence("111", zygosity=Zygosity.BIALLELIC, has_association=False)
        self._add_evidence("222", zygosity=Zygosity.BIALLELIC)
        summary = build_scoring_summary(self.curation)
        self.assertEqual(self._step(summary, "1C").total, 2 * Points.S1C_BIALLELIC)

    def test_counted_applies_each_publications_multipliers(self):
        self._add_evidence("111", num_fields=NumFields.FOUR)
        self._add_evidence("222", num_fields=NumFields.FOUR, has_association=False)
        self._add_evidence("333", num_fields=NumFields.ONE)
        allele = self._category(
            build_scoring_summary(self.curation), "Allele / haplotype"
        )
        self.assertEqual(
            allele.counted,
            Points.S1B_4_FIELD + Points.S1B_1_FIELD * Points.S6B_1_FIELD,
        )

    def test_total_score_matches_the_curation_score(self):
        self._add_evidence(
            "111",
            typing_method=TypingMethod.WHOLE_GENOME_SEQ,
            cohort_size=600,
            p_value=Decimal("0.00001"),
        )
        self._add_evidence("222", num_fields=NumFields.ONE, phase_confirmed=True)
        self._add_evidence("333", has_association=False, cohort_size=100)
        summary = build_scoring_summary(self.curation)
        self.assertGreater(summary.total_score, 0)
        self.assertAlmostEqual(summary.total_score, self.curation.score)

    def test_leaves_out_excluded_evidence(self):
        self._add_evidence("111", is_included=False)
        summary = build_scoring_summary(self.curation)
        self.assertEqual(summary.num_publications, 0)
        self.assertEqual(self._row(summary, "1A", Points.S1A_ALLELE).count, 0)

    def test_p_value_thresholds_use_the_interface_decimal_format(self):
        summary = build_scoring_summary(self.curation)
        label = self._row(summary, "3A", Points.S3A_INTERVAL_3).label
        threshold = format_decimal(Intervals.S3A.GWAS_3.end)
        self.assertIn("E", threshold)
        self.assertEqual(
            label, f"<{threshold} / <{format_decimal(Intervals.S3A.NON_GWAS_3.end)}"
        )

    def test_uses_the_scoring_matrix_labels(self):
        summary = build_scoring_summary(self.curation)
        steps = [s.label for c in summary.categories[1:] for s in c.steps]
        matrix_steps = [
            text
            for row in FRAMEWORK
            if isinstance(text := row.get("text"), str) and text.startswith("Step")
        ]
        self.assertEqual(steps, matrix_steps)
        labels = {r.label for c in summary.categories for s in c.steps for r in s.rows}
        for row in FRAMEWORK:
            if isinstance(category := row.get("category"), str):
                with self.subTest(category=category):
                    self.assertIn(category.strip(), labels)

    def test_cohort_thresholds_show_closed_brackets_as_ranges(self):
        summary = build_scoring_summary(self.curation)
        label = self._row(summary, "4", Points.S4_INTERVAL_2).label
        gwas = Intervals.S4.GWAS_2
        self.assertTrue(
            label.startswith(
                f"{format_decimal(gwas.start)}\N{EN DASH}{format_decimal(gwas.end)} / "
            )
        )

    def test_effect_size_max_is_both_categories(self):
        summary = build_scoring_summary(self.curation)
        self.assertEqual(
            self._step(summary, "3C").max_points,
            Points.S3C_OR_RR_BETA + Points.S3C_CI_DOES_NOT_CROSS,
        )

    def test_multiplier_note_counts_x1_and_lists_other_pmids(self):
        self._add_evidence("111")
        self._add_evidence("222")
        self._add_evidence("333", has_association=False)
        self._add_evidence("444", num_fields=NumFields.ONE)
        multipliers = self._category(
            build_scoring_summary(self.curation), "Multipliers"
        )
        self.assertEqual(
            multipliers.note,
            "Applied per publication; \N{MULTIPLICATION SIGN}1 in 2 studies; "
            "\N{MULTIPLICATION SIGN}0.5 in PMID: 444; \N{MULTIPLICATION SIGN}0 in "
            "PMID: 333",
        )

    def test_multiplier_note_without_evidence(self):
        multipliers = self._category(
            build_scoring_summary(self.curation), "Multipliers"
        )
        self.assertEqual(multipliers.note, "Applied per publication")


class BuildEvidenceScoringSummaryTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
        )

    def _add_evidence(self, pubmed_id: str, **fields) -> Evidence:
        publication, _ = Publication.objects.get_or_create(
            pubmed_id=pubmed_id, defaults={"slug": f"P{pubmed_id}"}
        )
        defaults = {
            "is_included": True,
            "num_fields": NumFields.FOUR,
            "has_association": True,
        }
        return Evidence.objects.create(
            curation=self.curation, publication=publication, **(defaults | fields)
        )

    def test_header_names_the_pair(self):
        summary = build_evidence_scoring_summary(self.curation)
        self.assertEqual(summary.subject_type, "Allele")
        self.assertEqual(summary.subject, self.allele.display_name)
        self.assertEqual(summary.car_id, self.allele.car_id)
        self.assertEqual(summary.disease, self.disease.name)
        self.assertEqual(summary.mondo_id, self.disease.mondo_id)

    def test_has_a_column_for_every_score_attribute(self):
        summary = build_evidence_scoring_summary(self.curation)
        attrs = {
            score
            for row in FRAMEWORK
            if isinstance(score := row.get("score"), str)
            and score.startswith("score_step_")
        }
        self.assertEqual(len(summary.columns), len(attrs))

    def test_one_row_per_included_evidence_item_in_order(self):
        self._add_evidence("111")
        self._add_evidence("222", is_included=False)
        self._add_evidence("333")
        rows = build_evidence_scoring_summary(self.curation).rows
        self.assertEqual([row.pmid for row in rows], ["111", "333"])

    def test_row_has_each_steps_points_and_the_evidence_score(self):
        evidence = self._add_evidence(
            "111",
            typing_method=TypingMethod.SANGER_SEQ,
            cohort_size=600,
            p_value=Decimal("0.00001"),
            num_fields=NumFields.ONE,
        )
        row = build_evidence_scoring_summary(self.curation).rows[0]
        points = dict(
            zip(
                build_evidence_scoring_summary(self.curation).columns,
                row.points,
                strict=True,
            )
        )
        self.assertEqual(points["1B"], evidence.score_step_1b)
        self.assertEqual(points["2"], evidence.score_step_2)
        self.assertEqual(points["6B"], evidence.score_step_6b)
        self.assertIsNone(points["3B"])
        self.assertEqual(row.total, evidence.score)
