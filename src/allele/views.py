"""Provides views for the allele app."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView

from allele.clients import fetch_allele_data, get_car_id
from allele.forms import AlleleForm
from allele.models import Allele
from core.permissions import CreateAccessMixin
from datatable.constants import FieldTypes, SortDirections
from datatable.views import datatable


class AlleleCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) an allele."""

    model = Allele
    form_class = AlleleForm
    template_name = "allele/create.html"

    def form_valid(self, form: AlleleForm) -> HttpResponse:
        """Fetches and adds data from the ClinGen Allele Registry and records user.

        Returns:
             The details page for the allele if the form is valid, or the form with
             errors if the form isn't valid.
        """
        allele_data = fetch_allele_data(form.instance.name)
        if allele_data:
            form.instance.car_id = get_car_id(allele_data)
            form.instance.added_by = self.request.user
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from the "
            "ClinGen Allele Registry. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("allele-create")


class AlleleDetail(DetailView):
    """Shows user information about an allele."""

    model = Allele
    template_name = "allele/detail.html"


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


def allele_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching alleles."""
    return datatable(
        request=request,
        model=Allele,
        order_by="pk",
        fields=FIELDS,
        data_title="Alleles",
        partial="allele/partials/search.html",
    )
