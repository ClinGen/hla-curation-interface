"""Provides views for the disease app."""

from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView, DetailView

from core.permissions import CreateAccessMixin
from datatable.constants import FieldTypes, SortDirections
from datatable.views import datatable
from disease.forms import DiseaseForm
from disease.models import Disease


class DiseaseCreateView(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a disease."""

    model = Disease
    form_class = DiseaseForm
    template_name = "disease/create.html"


class DiseaseDetailView(DetailView):
    """Shows user information about a disease."""

    model = Disease
    template_name = "disease/detail.html"


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
        "text": "Mondo ID",
        "param_name": "mondo_id",
        "id": "mondo-id",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Name",
        "param_name": "name",
        "id": "disease-name",
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


def disease_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching diseases."""
    return datatable(
        request=request,
        model=Disease,
        order_by="pk",
        fields=FIELDS,
        data_title="Diseases",
        partial="disease/partials/search.html",
    )
