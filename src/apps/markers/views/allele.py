"""Provide a views for alleles."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.markers.clients.allele import AlleleClient
from apps.markers.forms.allele import AlleleForm
from apps.markers.services.allele import AlleleService
from base.views import EntityView
from constants import IPDConstants


class AlleleView(EntityView):
    """Create, view all, or view an allele."""

    def new(self, request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates an allele."""
        if request.method == "POST":
            form = AlleleForm(request.POST)
            if form.is_valid():
                descriptor = form.cleaned_data["descriptor"]
                client = AlleleClient(descriptor)
                service = AlleleService(client)
                service.create(descriptor)
                return redirect("home")
        else:
            form = AlleleForm()
        return render(
            request,
            "markers/allele/new.html",
            {"form": form, "ipd_search_url": IPDConstants.SEARCH_URL},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    def list(self, request: HttpRequest) -> None:  # type: ignore
        """Return the searchable table page for an allele."""

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    def details(self, request: HttpRequest, human_readable_id: str) -> None:  # type: ignore
        """Return the details page for an allele."""
