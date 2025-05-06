"""Define the parameters for the tabs in the publications views."""

PUBMED_NEW_URL = "/publications/pubmed/new"
PUBMED_SEARCH_URL = "/publications/pubmed/list"
BIORXIV_NEW_URL = "/publications/biorxiv/new"
BIORXIV_SEARCH_URL = "/publications/biorxiv/list"
MEDRXIV_NEW_URL = "/publications/medrxiv/new"
MEDRXIV_SEARCH_URL = "/publications/medrxiv/list"

new_pubmed_publication_tabs = [
    {
        "text": "New PubMed Article",
        "is_active": True,
        "url": PUBMED_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New bioRxiv Paper",
        "is_active": False,
        "url": BIORXIV_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New medRxiv Paper",
        "is_active": False,
        "url": MEDRXIV_NEW_URL,
        "url_is_boosted": True,
    },
]

new_biorxiv_publication_tabs = [
    {
        "text": "New PubMed Article",
        "is_active": False,
        "url": PUBMED_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New bioRxiv Paper",
        "is_active": True,
        "url": BIORXIV_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New medRxiv Paper",
        "is_active": False,
        "url": MEDRXIV_NEW_URL,
        "url_is_boosted": True,
    },
]

new_medrxiv_publication_tabs = [
    {
        "text": "New PubMed Article",
        "is_active": False,
        "url": PUBMED_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New bioRxiv Paper",
        "is_active": False,
        "url": BIORXIV_NEW_URL,
        "url_is_boosted": True,
    },
    {
        "text": "New medRxiv Paper",
        "is_active": True,
        "url": MEDRXIV_NEW_URL,
        "url_is_boosted": True,
    },
]

search_pubmed_publication_tabs = [
    {
        "text": "Search PubMed Articles",
        "is_active": True,
        "url": PUBMED_NEW_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search bioRxiv Papers",
        "is_active": False,
        "url": BIORXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search medRxiv Papers",
        "is_active": False,
        "url": MEDRXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
]

search_biorxiv_publication_tabs = [
    {
        "text": "Search PubMed Articles",
        "is_active": False,
        "url": PUBMED_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search bioRxiv Papers",
        "is_active": True,
        "url": BIORXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search medRxiv Papers",
        "is_active": False,
        "url": MEDRXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
]

search_medrxiv_publication_tabs = [
    {
        "text": "Search PubMed Articles",
        "is_active": False,
        "url": PUBMED_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search bioRxiv Papers",
        "is_active": False,
        "url": BIORXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
    {
        "text": "Search medRxiv Papers",
        "is_active": True,
        "url": MEDRXIV_SEARCH_URL,
        "url_is_boosted": False,
    },
]
