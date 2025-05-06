"""Provide views for medRxiv publications."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.publications.components.params.tabs import (
    new_medrxiv_publication_tabs,
    search_medrxiv_publication_tabs,
)
from base.views import EntityView


class RxivMedView(EntityView):
    """Create, view all, or view a medRxiv publication."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a medRxiv publication."""
        return render(
            request,
            "publications/medrxiv/new.html",
            {"tabs": new_medrxiv_publication_tabs},
        )

    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for a PubMed publication."""
        return render(
            request,
            "publications/medrxiv/list.html",
            {"tabs": search_medrxiv_publication_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a PubMed publication."""
