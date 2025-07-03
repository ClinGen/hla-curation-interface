"""Provides views for the haplotype app."""

from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from datatable.constants import FieldTypes, SortDirections
from datatable.views import datatable
from haplotype.forms import HaplotypeForm
from haplotype.models import Haplotype


class HaplotypeCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a haplotype."""

    model = Haplotype
    form_class = HaplotypeForm
    template_name = "haplotype/create.html"


class HaplotypeDetail(DetailView):
    """Shows the user information about a haplotype."""

    model = Haplotype
    template_name = "haplotype/detail.html"


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


def haplotype_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching haplotypes."""
    return datatable(
        request=request,
        model=Haplotype,
        order_by="pk",
        fields=FIELDS,  # type: ignore
        data_title="Haplotypes",
        partial="haplotype/partials/search.html",
    )
