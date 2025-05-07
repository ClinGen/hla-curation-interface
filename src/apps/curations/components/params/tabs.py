"""Defines the parameters for the tabs in the curation views.

These parameters are used in the `Tabs` component. See `src/components/tabs`.
"""

ALLELE_NEW_URL = "/curations/allele/new"
ALLELE_SEARCH_URL = "/curations/allele/list"
HAPLOTYPE_NEW_URL = "/curations/haplotype/new"
HAPLOTYPE_SEARCH_URL = "/curations/haplotype/list"

new_allele_curation_tabs = [
    {
        "text": "New Allele Curation",
        "is_active": True,
        "url": ALLELE_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New Haplotype Curation",
        "is_active": False,
        "url": HAPLOTYPE_NEW_URL,
        "url_is_boosted": True,
    },
]

new_haplotype_curation_tabs = [
    {
        "text": "New Allele Curation",
        "is_active": False,
        "url": ALLELE_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New Haplotype Curation",
        "is_active": True,
        "url": HAPLOTYPE_NEW_URL,
        "url_is_boosted": True,
    },
]

search_allele_curation_tabs = [
    {
        "text": "Search Allele Curations",
        "is_active": True,
        "url": ALLELE_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search Haplotype Curations",
        "is_active": False,
        "url": HAPLOTYPE_SEARCH_URL,
        "url_is_boosted": False,
    },
]

search_haplotype_curation_tabs = [
    {
        "text": "Search Allele Curations",
        "is_active": False,
        "url": ALLELE_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search Haplotype Curations",
        "is_active": True,
        "url": HAPLOTYPE_SEARCH_URL,
        "url_is_boosted": False,
    },
]
