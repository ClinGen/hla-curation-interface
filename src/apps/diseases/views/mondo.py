"""Provide views for Mondo diseases."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.diseases.clients.mondo import MondoClient
from apps.diseases.forms.mondo import MondoDiseaseForm
from apps.diseases.selectors.mondo import MondoSelector
from apps.diseases.services.mondo import MondoService
from base.views import EntityView
from constants import MondoConstants


class MondoView(EntityView):
    """Create, view all, or view a Mondo disease."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a Mondo disease."""
        if request.method == "POST":
            form = MondoDiseaseForm(request.POST)
            if form.is_valid():
                mondo_id = form.cleaned_data["mondo_id"]
                client = MondoClient(mondo_id)
                client.fetch()  # Fetch the data from the Mondo API.
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
    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:  # type: ignore
        """Return the searchable table page for a Mondo disease."""
        query = request.GET.get("q", None)
        selector = MondoSelector()
        diseases = selector.list(query)

        if request.htmx:  # type: ignore (This attribute is added by the django-htmx app.)
            template_name = "diseases/includes/mondo_table.html"
        else:
            template_name = "diseases/mondo/list.html"

        return render(request, template_name, {"diseases": diseases})

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a Mondo disease."""
