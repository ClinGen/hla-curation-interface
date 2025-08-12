"""Houses constants for the views module of the publication app."""

from datatable.constants.views import FieldTypes, Filters, SortDirections
from publication.constants.models import PublicationTypes

PUBLICATION_TYPE_OPTIONS = [
    Filters.DEFAULT,
    PublicationTypes.PUBMED,
    PublicationTypes.BIORXIV,
    PublicationTypes.MEDRXIV,
]

PUBLICATION_SEARCH_FIELDS = [
    {
        "text": "ID",
        "param_name": "pk",
        "id": "pk",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Type",
        "param_name": "publication_type",
        "id": "publication-type",
        "default_value": PUBLICATION_TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": PUBLICATION_TYPE_OPTIONS,
    },
    {
        "text": "Author",
        "param_name": "author",
        "id": "author",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Title",
        "param_name": "title",
        "id": "title",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Added",
        "param_name": "added_at",
        "id": "added-at",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
]
