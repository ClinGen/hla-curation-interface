"""Make sure all routes work.

This test makes sure routes work; it also serves as a way of documenting the various
routes in one centralized location.
"""

import pytest
from django.test import Client

# TODO(Liam): Uncomment routes below as they are implemented.  # noqa: FIX002, TD003, E501

# fmt: off
ROUTES = [
    # Home page.
    "/",

    # Mondo diseases: Create, view all, or view specific.
    "/diseases/mondo/new",
    # "/diseases/mondo/all",
    # "/diseases/mondo/<str:mondo_id>",

    # Alleles: Create, view all, or view specific.
    "/markers/allele/new",
    # "/markers/allele/all",
    # "/markers/allele/<str:car_id>",

    # Haplotypes: Create, view all, or view specific.
    # "/markers/haplotype/new",
    # "/markers/haplotype/all",
    # "/markers/haplotype/<str:car_id>",

    # PubMed publications: Create, view all, or view specific.
    "/publications/pubmed/new",
    "/publications/pubmed/all",
    # "/publications/pubmed/<str:pubmed_id>",

    # bioRxiv publications: Create, view all, or view specific.
    # "/publications/biorxiv/new",
    # "/publications/biorxiv/all",
    # "/publications/biorxiv/<str:doi>",

    # medRxiv publications: Create, view all, or view specific.
    # "/publications/medrxiv/new",
    # "/publications/medrxiv/all",
    # "/publications/medrxiv/<str:doi>",

    # Curations: Create, view all, or view specific.
    # "/curations/allele/new",
    # "/curations/allele/all",
    # "/curations/allele/<str:curation_id>",

    # Curations: Edit an allele classification.
    # "/curations/allele/<str:allele_curation_id>/edit",

    # Curations: Edit an allele association.
    # "/curations/allele/<str:allele_curation_id>/association/<str:allele_association_id>/edit",  # noqa: E501

    # Curations: Create, view all, or view specific.
    # "/curations/haplotype/new",
    # "/curations/haplotype/all",
    # "/curations/haplotype/<str:haplotype_curation_id>",

    # Curations: Edit a haplotype classification.
    # "/curations/haplotype/<str:haplotype_curation_id>/edit",

    # Curations: Edit a haplotype association.
    # "/curations/haplotype/<str:haplotype_curation_id>/association/<str:haplotype_association_id>/edit",  # noqa: E501
]
# fmt: on


@pytest.mark.integration
@pytest.mark.django_db
def test_all_routes_return_200(client: Client) -> None:
    """Make sure all routes return a 200 status code."""
    for route in ROUTES:
        response = client.get(route)
        assert response.status_code == 200, (
            f"Route test for {route} failed with status {response.status_code}"
        )
