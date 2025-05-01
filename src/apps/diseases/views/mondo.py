"""Provide views for Mondo diseases."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.diseases.clients.mondo import MondoClient
from apps.diseases.forms.mondo import MondoDiseaseForm
from apps.diseases.services.mondo import MondoService
from base.views import EntityView
from constants import MondoConstants


class MondoView(EntityView):
    """Create, view all, or view a Mondo disease."""

    def new(self, request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a Mondo disease."""
        if request.method == "POST":
            form = MondoDiseaseForm(request.POST)
            if form.is_valid():
                mondo_id = form.cleaned_data["mondo_id"]
                client = MondoClient(mondo_id)
                service = MondoService(client)
                service.create(mondo_id)
                return redirect("home")
        else:
            form = MondoDiseaseForm()
        return render(
            request,
            "diseases/mondo/new.html",
            {"form": form, "mondo_search_url": MondoConstants.SEARCH_URL},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    def list(self, request: HttpRequest) -> HttpResponse:  # type: ignore
        """Return the searchable table page for a Mondo disease."""

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    def details(self, request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a Mondo disease."""
