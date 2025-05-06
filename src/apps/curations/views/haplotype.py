"""Provide views for haplotype curations."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.curations.components.params.tabs import (
    new_haplotype_curation_tabs,
    search_haplotype_curation_tabs,
)
from base.views import EntityView


class HaplotypeCurationView(EntityView):
    """Create, view all, or view a haplotype curation."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a haplotype curation."""
        return render(
            request,
            "curations/haplotype/new.html",
            {"tabs": new_haplotype_curation_tabs},
        )

    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for a haplotype curation."""
        return render(
            request,
            "curations/haplotype/list.html",
            {"tabs": search_haplotype_curation_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a haplotype curation."""
