"""Define the parameters for the tabs in the curation views."""

new_allele_curation_tabs = [
    {
        "text": "New Allele Curation",
        "is_active": True,
        "url": "/curations/new",
        "url_is_boosted": True,
    },
    {
        "text": "New Haplotype Curation",
        "is_active": False,
        "url": "#",
        "url_is_boosted": True,
    },
]

search_allele_curation_tabs = [
    {
        "text": "Search Allele Curations",
        "is_active": True,
        "url": "/curations/list",
        "url_is_boosted": False,
    },
    {
        "text": "Search Haplotype Curations",
        "is_active": False,
        "url": "#",
        "url_is_boosted": False,
    },
]
