"""Tests our custom interval class."""

from decimal import Decimal
from unittest import TestCase

from curation.interval import Interval


class IntervalTest(TestCase):
    def setUp(self):
        self.start = Decimal("0.1")
        self.end = Decimal("0.3")
        self.inclusive_interval = Interval(
            start=self.start,
            end=self.end,
            start_inclusive=True,
            end_inclusive=True,
            variable="n",
        )
        self.exclusive_interval = Interval(
            start=self.start,
            end=self.end,
            start_inclusive=False,
            end_inclusive=False,
            variable="n",
        )
        self.mixed_interval_1 = Interval(
            start=self.start,
            end=self.end,
            start_inclusive=False,
            end_inclusive=True,
            variable="n",
        )
        self.mixed_interval_2 = Interval(
            start=self.start,
            end=self.end,
            start_inclusive=True,
            end_inclusive=False,
            variable="n",
        )

    def test_inclusive_contains_lower_boundary(self):
        self.assertTrue(self.inclusive_interval.contains(Decimal("0.1")))

    def test_inclusive_contains_middle(self):
        self.assertTrue(self.inclusive_interval.contains(Decimal("0.2")))

    def test_inclusive_contains_upper_boundary(self):
        self.assertTrue(self.inclusive_interval.contains(Decimal("0.3")))

    def test_exclusive_does_not_contain_lower_boundary(self):
        self.assertFalse(self.exclusive_interval.contains(Decimal("0.1")))

    def test_exclusive_contains_middle(self):
        self.assertTrue(self.exclusive_interval.contains(Decimal("0.2")))

    def test_exclusive_does_not_contain_upper_boundary(self):
        self.assertFalse(self.exclusive_interval.contains(Decimal("0.3")))

    def test_mixed_interval_1_does_not_contain_lower_boundary(self):
        self.assertFalse(self.mixed_interval_1.contains(Decimal("0.1")))

    def test_mixed_interval_1_contains_middle(self):
        self.assertTrue(self.mixed_interval_1.contains(Decimal("0.2")))

    def test_mixed_interval_1_contains_upper_boundary(self):
        self.assertTrue(self.mixed_interval_1.contains(Decimal("0.3")))

    def test_mixed_interval_2_does_not_contain_lower_boundary(self):
        self.assertTrue(self.mixed_interval_2.contains(Decimal("0.1")))

    def test_mixed_interval_2_contains_middle(self):
        self.assertTrue(self.mixed_interval_2.contains(Decimal("0.2")))

    def test_mixed_interval_2_contains_upper_boundary(self):
        self.assertFalse(self.mixed_interval_2.contains(Decimal("0.3")))
