"""Provides views for the curation app."""

from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from curation.forms import CurationForm
from curation.models import Curation, CurationTypes
from datatable.constants import FieldTypes, Filters, SortDirections
from datatable.views import datatable


class CurationCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a curation."""

    model = Curation
    form_class = CurationForm
    template_name = "curation/create.html"

    def form_valid(self, form: CurationForm) -> HttpResponse:
        """Makes sure the user who added the curation is recorded.

        Returns:
             The details page for the curation if the form is valid, or the form with
             errors if the form isn't valid.
        """
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class CurationDetail(DetailView):
    """Shows the user information about a curation."""

    model = Curation
    template_name = "curation/detail.html"


CURATION_TYPE_OPTIONS = [
    Filters.DEFAULT,
    CurationTypes.ALLELE,
    CurationTypes.HAPLOTYPE,
]

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
        "param_name": "curation_type",
        "id": "curation-type",
        "default_value": CURATION_TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": CURATION_TYPE_OPTIONS,
    },
    {
        "text": "Allele",
        "param_name": "allele",
        "id": "allele",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Haplotype",
        "param_name": "haplotype",
        "id": "haplotype",
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


def curation_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching curations."""
    return datatable(
        request=request,
        model=Curation,
        order_by="pk",
        fields=FIELDS,  # type: ignore
        data_title="Curations",
    )
