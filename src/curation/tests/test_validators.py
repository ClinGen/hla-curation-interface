"""Houses tests for the curation app's scoring module."""

from decimal import Decimal

from django.test import TestCase

from curation.constants.score import Intervals
from curation.validators.common import has_association_and_p_value_err_msg


class TestCommonValidators(TestCase):
    def test_gwas_p_value_at_threshold_is_not_significant(self):
        p_value = Intervals.S3A.GWAS_1.start
        self.assertIsNotNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=True,
                has_association=True,
            )
        )

    def test_gwas_p_value_above_threshold_is_not_significant(self):
        p_value = Intervals.S3A.GWAS_1.start + Decimal("0.01")
        self.assertIsNotNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=True,
                has_association=True,
            )
        )

    def test_gwas_p_value_below_threshold_is_significant(self):
        p_value = Intervals.S3A.GWAS_1.start - Decimal("0.01")
        self.assertIsNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=True,
                has_association=True,
            )
        )

    def test_gwas_p_value_much_smaller_is_significant(self):
        p_value = Decimal("1e-15")
        self.assertIsNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=True,
                has_association=True,
            )
        )

    def test_non_gwas_p_value_at_threshold_is_not_significant(self):
        p_value = Intervals.S3A.NON_GWAS_1.start
        self.assertIsNotNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=False,
                has_association=True,
            )
        )

    def test_non_gwas_p_value_above_threshold_is_not_significant(self):
        p_value = Intervals.S3A.NON_GWAS_1.start + Decimal("0.01")
        self.assertIsNotNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=False,
                has_association=True,
            )
        )

    def test_non_gwas_p_value_below_threshold_is_significant(self):
        p_value = Intervals.S3A.NON_GWAS_1.start - Decimal("0.01")
        self.assertIsNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=False,
                has_association=True,
            )
        )

    def test_non_gwas_p_value_much_smaller_is_significant(self):
        p_value = Decimal("1e-15")
        self.assertIsNone(
            has_association_and_p_value_err_msg(
                p_value,
                is_gwas=False,
                has_association=True,
            )
        )
