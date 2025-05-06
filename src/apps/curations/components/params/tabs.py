"""Define the parameters for the tabs in the curation views."""

new_allele_curation_tabs = [
    {
        "text": "New Allele Curation",
        "is_active": True,
        "url": "/curations/allele/new",
        "url_is_boosted": True,
    },
    {
        "text": "New Haplotype Curation",
        "is_active": False,
        "url": "/curations/haplotype/new",
        "url_is_boosted": True,
    },
]

new_haplotype_curation_tabs = [
    {
        "text": "New Allele Curation",
        "is_active": False,
        "url": "/curations/allele/new",
        "url_is_boosted": True,
    },
    {
        "text": "New Haplotype Curation",
        "is_active": True,
        "url": "/curations/haplotype/new",
        "url_is_boosted": True,
    },
]

search_allele_curation_tabs = [
    {
        "text": "Search Allele Curations",
        "is_active": True,
        "url": "/curations/allele/list",
        "url_is_boosted": False,
    },
    {
        "text": "Search Haplotype Curations",
        "is_active": False,
        "url": "/curations/haplotype/list",
        "url_is_boosted": False,
    },
]

search_haplotype_curation_tabs = [
    {
        "text": "Search Allele Curations",
        "is_active": False,
        "url": "/curations/allele/list",
        "url_is_boosted": False,
    },
    {
        "text": "Search Haplotype Curations",
        "is_active": True,
        "url": "/curations/haplotype/list",
        "url_is_boosted": False,
    },
]
