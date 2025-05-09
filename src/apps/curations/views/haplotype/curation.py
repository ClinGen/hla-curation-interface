"""Provides HTTP views for managing haplotype curations within the application.

This module is meant to handle primarily HTTP logic. Read logic should be delegated to
the relevant selectors module. Create and update logic should be delegated to the
relevant services module.

This module defines views for creating new haplotype curations, listing existing ones
with search functionality, and displaying detailed information for a specific
haplotype curation. These views handle user interactions, form processing,
data retrieval via selectors, and data manipulation via services related to
haplotype curations.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.curations.components.params.tabs import (
    new_haplotype_curation_tabs,
    search_haplotype_curation_tabs,
)
from base.views import EntityView


class HaplotypeCurationView(EntityView):
    """Encapsulates the primary interactions for haplotype curations.

    This class provides methods for:
        - Creating new haplotype curations based on user input.
        - Displaying a searchable list of existing haplotype curations.
        - Showing detailed information for a specific haplotype curation.
    """

    # TODO(Liam): Implement this method.  # noqa: FIX002, TD003
    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Renders the new allele curation form and handles the form's submission.

        The view uses the `new_haplotype_curation_tabs` context variable to render
        navigation tabs on the page.

        Args:
            request: The Django `HttpRequest` object.

        Returns:
            A Django `HttpResponse` object rendering the form.
        """
        return render(
            request,
            "curations/haplotype/new.html",
            {"tabs": new_haplotype_curation_tabs},
        )

    # TODO(Liam): Implement this method.  # noqa: FIX002, TD003
    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Renders a searchable list of haplotype curations.

        The view uses the `search_haplotype_curation_tabs` context variable to render
        navigation tabs on the page.

        Args:
            request: The Django `HttpRequest` object. The GET parameters may include `q`
                for filtering the curations.

        Returns:
            A Django `HttpResponse` object that renders the list of allele curations.
        """
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
        """Renders the details page for a specific allele curation.

        Args:
            request: The Django `HttpRequest` object.
            human_readable_id: A string that uniquely identifies the allele
                curation for display, AKA the curation ID.

        Returns:
            A Django `HttpResponse` object that renders the allele curation's details
                page.
        """
