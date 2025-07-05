"""Provides views for the disease app."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView

from core.permissions import CreateAccessMixin
from datatable.constants import FieldTypes, SortDirections
from datatable.views import datatable
from disease.clients import fetch_disease_data, get_iri, get_name
from disease.forms import DiseaseForm
from disease.models import Disease


class DiseaseCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a disease."""

    model = Disease
    form_class = DiseaseForm
    template_name = "disease/create.html"

    def form_valid(self, form: DiseaseForm) -> HttpResponse:
        """Fetches and adds data from the Ontology Lookup Service and records user.

        Returns:
             The details page for the allele if the form is valid, or the form with
             errors if the form isn't valid.
        """
        disease_data = fetch_disease_data(form.instance.mondo_id)
        if disease_data:
            form.instance.name = get_name(disease_data)
            form.instance.iri = get_iri(disease_data)
            form.instance.added_by = self.request.user
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from the "
            "Ontology Lookup Service. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("disease-create")


class DiseaseDetail(DetailView):
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
