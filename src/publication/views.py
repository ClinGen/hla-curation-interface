"""Provides views for the publication app."""

from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from datatable.constants import FieldTypes, Filters, SortDirections
from datatable.views import datatable
from publication.forms import PublicationForm
from publication.models import Publication, PublicationTypes


class PublicationCreateView(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a publication."""

    model = Publication
    form_class = PublicationForm
    template_name = "publication/create.html"


class PublicationDetailView(DetailView):
    """Shows the user information about a publication."""

    model = Publication
    template_name = "publication/detail.html"


PUBLICATION_TYPE_OPTIONS = [
    Filters.DEFAULT,
    PublicationTypes.PUBMED,
    PublicationTypes.BIORXIV,
    PublicationTypes.MEDRXIV,
]

# Define fields for use in the datatable.
FIELDS = [
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


def publication_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching publications."""
    return datatable(
        request=request,
        model=Publication,
        order_by="pk",
        fields=FIELDS,  # type: ignore
        data_title="Publications",
        partial="publication/partials/search.html",
    )
