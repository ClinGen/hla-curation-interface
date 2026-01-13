"""Defines constants for the repo app's views."""

from typing import Any

from curation.constants.views import CURATION_TYPE_OPTIONS
from datatable.constants.views import FieldTypes, SortDirections

PUBLISHED_CURATION_SEARCH_FIELDS: list[dict[str, Any]] = [
    {
        "text": "Curation ID",
        "param_name": "curation__slug",
        "id": "curation-slug",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Type",
        "param_name": "curation__curation_type",
        "id": "curation-type",
        "default_value": CURATION_TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": CURATION_TYPE_OPTIONS,
    },
    {
        "text": "Allele",
        "param_name": "curation__allele",
        "is_foreign_key": True,
        "id": "allele-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Haplotype",
        "param_name": "curation__haplotype",
        "is_foreign_key": True,
        "id": "haplotype-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Disease",
        "param_name": "curation__disease",
        "is_foreign_key": True,
        "id": "disease-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Published",
        "param_name": "published_at",
        "id": "published-at",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
]
