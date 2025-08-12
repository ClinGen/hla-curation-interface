"""Provides views for the publication app."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from datatable.constants.views import FieldTypes, Filters, SortDirections
from datatable.views import datatable
from publication.clients import (
    fetch_pubmed_data,
    fetch_rxiv_data,
    get_pubmed_author,
    get_pubmed_title,
    get_rxiv_author,
    get_rxiv_title,
)
from publication.forms import PublicationForm
from publication.models import Publication, PublicationTypes


class PublicationCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a publication."""

    model = Publication
    form_class = PublicationForm
    template_name = "publication/create.html"

    def form_valid(self, form: PublicationForm) -> HttpResponse:
        """Makes sure the user who added the publication is recorded.

        Returns:
             The details page for the publication if the form is valid, or the form with
             errors if the form isn't valid.
        """
        if form.instance.publication_type == PublicationTypes.PUBMED:
            pubmed_data = fetch_pubmed_data(form.instance.pubmed_id)
            if pubmed_data:
                form.instance.author = get_pubmed_author(pubmed_data)
                form.instance.title = get_pubmed_title(pubmed_data)
                form.instance.added_by = self.request.user
                return super().form_valid(form)
        elif (
            form.instance.publication_type == PublicationTypes.BIORXIV
            or form.instance.publication_type == PublicationTypes.MEDRXIV
        ):
            rxiv_data = fetch_rxiv_data(
                form.instance.publication_type, form.instance.doi
            )
            if rxiv_data:
                form.instance.author = get_rxiv_author(rxiv_data)
                form.instance.title = get_rxiv_title(rxiv_data)
                form.instance.added_by = self.request.user
                return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from PubMed. "
            "Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("disease-create")


class PublicationDetail(DetailView):
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
