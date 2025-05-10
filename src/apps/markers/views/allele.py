"""Provide a views for alleles."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.markers.clients.allele import AlleleClient
from apps.markers.forms.allele import AlleleForm
from apps.markers.selectors.allele import AlleleSelector
from apps.markers.services.allele import AlleleService
from base.views import EntityView
from constants import IPDConstants


class AlleleView(EntityView):
    """Create, view all, or view an allele."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates an allele."""
        if request.method == "POST":
            form = AlleleForm(request.POST)
            if form.is_valid():
                descriptor = form.cleaned_data["descriptor"]
                client = AlleleClient(descriptor)
                client.fetch()
                service = AlleleService(client)
                service.create(descriptor)
                messages.success(request, "Allele created.")
                form = AlleleForm()
        else:
            form = AlleleForm()
        return render(
            request,
            "markers/allele/new.html",
            {"form": form, "ipd_search_url": IPDConstants.SEARCH_URL},
        )

    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for an allele."""
        query = request.GET.get("q", None)
        selector = AlleleSelector()
        alleles = selector.list(query)

        if request.htmx:  # type: ignore (This attribute is added by the django-htmx app.)
            template_name = "markers/includes/allele_table.html"
        else:
            template_name = "markers/allele/list.html"

        return render(request, template_name, {"alleles": alleles})

    @staticmethod
    def details(request: HttpRequest, car_id: str) -> HttpResponse:
        """Return the details page for an allele."""
        selector = AlleleSelector()
        allele = selector.get(car_id=car_id)
        context = {"allele": allele}
        return render(request, "markers/allele/details.html", context)
