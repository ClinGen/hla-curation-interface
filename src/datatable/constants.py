"""Provides constants for use in datatable views."""


class FieldTypes:
    """Defines the string values for the types of columns in a datatable."""

    SEARCH = "search"
    SORT = "sort"
    FILTER = "filter"


class SortDirections:
    """Defines the string values for sort directions."""

    ASCENDING = "asc"
    DESCENDING = "desc"
    DEFAULT = "none"


class Filters:
    """Defines the default and none values for filtering."""

    DEFAULT = "any"  # When you don't want a filter.
    NONE = "none"  # When you want to filter on a value of none/empty/null.
