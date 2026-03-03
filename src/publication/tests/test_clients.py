# type: ignore
"""API contract tests for publication clients.

These tests make real API calls to PubMed, bioRxiv, and medRxiv to verify
the client functions work correctly. They are skipped by default to avoid
hitting external APIs during regular test runs.

To run these tests, set the environment variable RUN_CONTRACT_TESTS=1:
    RUN_CONTRACT_TESTS=1 just test-all

When you run these tests, you might see DEBUG logs, depending on how you've configured
your logger. If you don't want the DEBUG logs, set the logger to the WARNING level.
"""

import os
import unittest

from publication.clients import (
    fetch_pubmed_data,
    fetch_rxiv_data,
    get_pubmed_author,
    get_pubmed_title,
    get_pubmed_year,
    get_rxiv_author,
    get_rxiv_title,
    get_rxiv_year,
)
from publication.constants.models import PublicationTypes

SKIP_CONTRACT_TESTS = os.getenv("RUN_CONTRACT_TESTS") != "1"
SKIP_REASON = "Contract tests are skipped by default. Set RUN_CONTRACT_TESTS=1 to run."

PUBMED_TEST_CASES = [
    {
        "pubmed_id": "38226399",
        "expected_title": (
            "Complete HLA genotyping of type 1 diabetes patients and controls from "
            "Mali reveals both expected and novel disease associations"
        ),
        "expected_author": "Noble",
        "expected_year": 2024,
    },
    {
        "pubmed_id": "36062396",
        "expected_title": (
            "Clinical features, biochemistry, and HLA-DRB1 status in "
            "youth-onset type 1 diabetes in Mali"
        ),
        "expected_author": "Besançon",
        "expected_year": 2022,
    },
    {
        "pubmed_id": "35419034",
        "expected_title": (
            "HLA-DRB1 and -DQB1 Alleles, Haplotypes and Genotypes in Emirati Patients "
            "with Type 1 Diabetes Underscores the Benefits of Evaluating Understudied "
            "Populations"
        ),
        "expected_author": "Al Yafei",
        "expected_year": 2022,
    },
]

BIORXIV_TEST_CASES = [
    {
        "doi": "10.64898/2026.02.15.706040",
        "expected_title_contains": "glaucoma",
        "expected_author_contains": "Ishimoto",
        "expected_year": 2026,
    },
    {
        "doi": "10.64898/2026.02.17.706411",
        "expected_title_contains": "schizophrenia",
        "expected_author_contains": "Moyer",
        "expected_year": 2026,
    },
]

MEDRXIV_TEST_CASES = [
    {
        "doi": "10.64898/2026.02.08.26345868",
        "expected_title_contains": "Monogenic",
        "expected_author_contains": "Guyler",
        "expected_year": 2026,
    },
    {
        "doi": "10.64898/2026.02.10.26344393",
        "expected_title_contains": (
            "Genomics link obesity and type 2 diabetes to "
            "Alzheimer's disease to unveil novel biological insights"
        ),
        "expected_author_contains": "Cunha",
        "expected_year": 2026,
    },
]


@unittest.skipIf(SKIP_CONTRACT_TESTS, SKIP_REASON)
class PubMedContractTest(unittest.TestCase):
    def test_fetch_pubmed_data_returns_soup(self) -> None:
        for test_case in PUBMED_TEST_CASES:
            with self.subTest(pubmed_id=test_case["pubmed_id"]):
                soup = fetch_pubmed_data(test_case["pubmed_id"])
                self.assertIsNotNone(
                    soup,
                    f"Failed to fetch data for PubMed ID {test_case['pubmed_id']}",
                )

    def test_get_pubmed_title_extracts_title(self) -> None:
        for test_case in PUBMED_TEST_CASES:
            with self.subTest(pubmed_id=test_case["pubmed_id"]):
                soup = fetch_pubmed_data(test_case["pubmed_id"])
                self.assertIsNotNone(soup)
                title = get_pubmed_title(soup)  # type: ignore[arg-type]
                self.assertIn(
                    test_case["expected_title"],
                    title,
                    f"Title mismatch for PubMed ID {test_case['pubmed_id']}",
                )

    def test_get_pubmed_author_extracts_author(self) -> None:
        for test_case in PUBMED_TEST_CASES:
            with self.subTest(pubmed_id=test_case["pubmed_id"]):
                soup = fetch_pubmed_data(test_case["pubmed_id"])
                self.assertIsNotNone(soup)
                author = get_pubmed_author(soup)  # type: ignore[arg-type]
                self.assertEqual(
                    test_case["expected_author"],
                    author,
                    f"Author mismatch for PubMed ID {test_case['pubmed_id']}",
                )

    def test_get_pubmed_year_extracts_year(self) -> None:
        for test_case in PUBMED_TEST_CASES:
            with self.subTest(pubmed_id=test_case["pubmed_id"]):
                soup = fetch_pubmed_data(test_case["pubmed_id"])
                self.assertIsNotNone(soup)
                year = get_pubmed_year(soup)  # type: ignore[arg-type]
                self.assertEqual(
                    test_case["expected_year"],
                    year,
                    f"Year mismatch for PubMed ID {test_case['pubmed_id']}",
                )


@unittest.skipIf(SKIP_CONTRACT_TESTS, SKIP_REASON)
class BioRxivContractTest(unittest.TestCase):
    def test_fetch_rxiv_data_returns_dict(self) -> None:
        for test_case in BIORXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.BIORXIV, test_case["doi"])
                self.assertIsNotNone(
                    data,
                    f"Failed to fetch data for bioRxiv DOI {test_case['doi']}",
                )
                self.assertIsInstance(data, dict)
                self.assertIn("collection", data)

    def test_get_rxiv_title_extracts_title(self) -> None:
        for test_case in BIORXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.BIORXIV, test_case["doi"])
                self.assertIsNotNone(data)
                title = get_rxiv_title(data)  # type: ignore[arg-type]
                self.assertIn(
                    test_case["expected_title_contains"],
                    title,
                    f"Title missing expected text for bioRxiv DOI {test_case['doi']}",
                )

    def test_get_rxiv_author_extracts_author(self) -> None:
        for test_case in BIORXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.BIORXIV, test_case["doi"])
                self.assertIsNotNone(data)
                author = get_rxiv_author(data)  # type: ignore[arg-type]
                self.assertIn(
                    test_case["expected_author_contains"],
                    author,
                    f"Author missing expected text for bioRxiv DOI {test_case['doi']}",
                )

    def test_get_rxiv_year_extracts_year(self) -> None:
        for test_case in BIORXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.BIORXIV, test_case["doi"])
                self.assertIsNotNone(data)
                year = get_rxiv_year(data)  # type: ignore[arg-type]
                self.assertEqual(
                    test_case["expected_year"],
                    year,
                    f"Year mismatch for bioRxiv DOI {test_case['doi']}",
                )


@unittest.skipIf(SKIP_CONTRACT_TESTS, SKIP_REASON)
class MedRxivContractTest(unittest.TestCase):
    def test_fetch_rxiv_data_returns_dict(self) -> None:
        for test_case in MEDRXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.MEDRXIV, test_case["doi"])
                self.assertIsNotNone(
                    data,
                    f"Failed to fetch data for medRxiv DOI {test_case['doi']}",
                )
                self.assertIsInstance(data, dict)
                self.assertIn("collection", data)

    def test_get_rxiv_title_extracts_title(self) -> None:
        for test_case in MEDRXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.MEDRXIV, test_case["doi"])
                self.assertIsNotNone(data)
                title = get_rxiv_title(data)  # type: ignore[arg-type]
                self.assertIn(
                    test_case["expected_title_contains"],
                    title,
                    f"Title missing expected text for medRxiv DOI {test_case['doi']}",
                )

    def test_get_rxiv_author_extracts_author(self) -> None:
        for test_case in MEDRXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.MEDRXIV, test_case["doi"])
                self.assertIsNotNone(data)
                author = get_rxiv_author(data)  # type: ignore[arg-type]
                self.assertIn(
                    test_case["expected_author_contains"],
                    author,
                    f"Author missing expected text for medRxiv DOI {test_case['doi']}",
                )

    def test_get_rxiv_year_extracts_year(self) -> None:
        for test_case in MEDRXIV_TEST_CASES:
            with self.subTest(doi=test_case["doi"]):
                data = fetch_rxiv_data(PublicationTypes.MEDRXIV, test_case["doi"])
                self.assertIsNotNone(data)
                year = get_rxiv_year(data)  # type: ignore[arg-type]
                self.assertEqual(
                    test_case["expected_year"],
                    year,
                    f"Year mismatch for medRxiv DOI {test_case['doi']}",
                )
