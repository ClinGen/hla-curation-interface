"""Houses constants used in the allele app's views module."""

from datatable.constants.views import FieldTypes, SortDirections

ALLELE_SEARCH_FIELDS = [
    {
        "text": "ID",
        "param_name": "slug",
        "id": "slug",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Name",
        "param_name": "name",
        "id": "allele-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "CAR ID",
        "param_name": "car_id",
        "id": "car-id",
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
