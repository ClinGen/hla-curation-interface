"""Provides functions for searching, sorting, and filtering a QuerySet."""

from django.db.models import Q, QuerySet
from django.http import HttpRequest

from datatable.constants.views import Filters, SortDirections


def search(
    request: HttpRequest,
    queryset: QuerySet,
    param_name: str,
    field_name: str | None = None,
) -> QuerySet:
    """Searches the given QuerySet for the given search term.

    Args:
        request: The HttpRequest object.
        queryset: The QuerySet to search.
        param_name: The name of the parameter in the GET request containing the search
                    term.
        field_name: The name of the field in the model to search on. This parameter is
                    optional. If it isn't supplied, we will assume the param_name is
                    the name of the field in the model to filter on.

    Returns:
        The QuerySet containing the search results.
    """
    field_name = field_name if field_name else param_name
    search_term = request.GET.get(param_name)
    if search_term:
        q = Q(**{f"{field_name}__icontains": search_term})
        queryset = queryset.filter(q)
    return queryset


def sort(request: HttpRequest, queryset: QuerySet, field_name: str) -> QuerySet:
    """Returns the QuerySet sorted according to the request's query parameters.

    Args:
        request: The HttpRequest object.
        queryset: The QuerySet to sort.
        field_name: The name of the field in the model to sort.
    """
    sort_dir = request.GET.get(field_name)
    if sort_dir in [SortDirections.ASCENDING, SortDirections.DESCENDING]:
        dir_prefix = "-" if sort_dir == SortDirections.DESCENDING else ""
        queryset = queryset.order_by(f"{dir_prefix}{field_name}")
    return queryset


def filter_(
    request: HttpRequest,
    queryset: QuerySet,
    param_name: str,
    field_name: str | None = None,
    none_value: str | None = "",
) -> QuerySet:
    """Applies a filter to the given QuerySet.

    Args:
        request: The HttpRequest object.
        queryset: The QuerySet to filter.
        param_name: The name of the parameter in the GET request containing the filter
                    term.
        field_name: The name of the field in the model to filter on. This parameter is
                    optional. If it isn't supplied, we will assume the param_name is
                    the name of the field in the model to filter on.
        none_value: The value to filter on when the user specifically wants to filter on
                    objects that are none/null/empty.

    Returns:
        The filtered QuerySet.
    """
    field_name = field_name if field_name else param_name
    value = request.GET.get(param_name)
    if value:
        if value == Filters.DEFAULT:
            pass
        elif value == Filters.NONE:
            queryset = queryset.filter(**{field_name: none_value})
        else:
            queryset = queryset.filter(**{field_name: value})
    return queryset
