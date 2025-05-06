"""Provide views for curations."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.curations.components.params.tabs import (
    new_allele_curation_tabs,
    search_allele_curation_tabs,
)
from apps.curations.forms.curation import CurationForm
from apps.curations.selectors.curation import AlleleCurationSelector
from apps.curations.services.curation import AlleleCurationService
from base.views import EntityView


class CurationView(EntityView):
    """Create, view all, or view a curation."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a curation."""
        if request.method == "POST":
            form = CurationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                service = AlleleCurationService()
                service.create(data["disease"], data["allele"])
                messages.success(request, "Curation created.")
                form = CurationForm()
        else:
            form = CurationForm()
        return render(
            request,
            "curations/new.html",
            {"form": form, "tabs": new_allele_curation_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:  # type: ignore
        """Return the searchable table page for a PubMed publication."""
        query = request.GET.get("q", None)
        selector = AlleleCurationSelector()
        curations = selector.list(query)

        if request.htmx:  # type: ignore (This attribute is added by the django-htmx app.)
            template_name = "curations/includes/curation_table.html"
        else:
            template_name = "curations/list.html"

        return render(
            request,
            template_name,
            {"curations": curations, "tabs": search_allele_curation_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a PubMed publication."""
