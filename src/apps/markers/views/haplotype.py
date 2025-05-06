"""Provide a views for haplotypes."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from base.views import EntityView


class HaplotypeView(EntityView):
    """Create, view all, or view a haplotype."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a haplotype."""
        return render(request, "markers/haplotype/new.html")

    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for haplotypes."""
        return render(request, "markers/haplotype/list.html")

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> None:  # type: ignore
        """Return the details page for an allele."""
