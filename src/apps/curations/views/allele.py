"""Provides HTTP views for managing allele curations within the application.

This module is meant to handle primarily HTTP logic. Read logic should be delegated to
the relevant selectors module. Create and update logic should be delegated to the
relevant services module.

This module defines views for creating new allele curations, listing existing ones
with search functionality, and displaying detailed information for a specific
allele curation. These views handle user interactions, form processing,
data retrieval via selectors, and data manipulation via services related to
allele curations.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.curations.components.params.tabs import (
    new_allele_curation_tabs,
    search_allele_curation_tabs,
)
from apps.curations.forms.allele import AlleleCurationForm
from apps.curations.selectors.allele import AlleleCurationSelector
from apps.curations.services.allele import AlleleCurationService
from base.views import EntityView


class AlleleCurationView(EntityView):
    """Encapsulates the primary interactions for allele curations.

    This class provides methods for:
        - Creating new allele curations based on user input.
        - Displaying a searchable list of existing allele curations.
        - Showing detailed information for a specific allele curation.
    """

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Renders the new allele curation form and handles the form's submission.

        The view uses the `new_allele_curation_tabs` context variable to render
        navigation tabs on the page.

        Args:
            request: The Django `HttpRequest` object.

        Returns:
            A Django `HttpResponse` object rendering the form.
        """
        if request.method == "POST":
            form = AlleleCurationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                service = AlleleCurationService()
                curation = service.create(data["disease"], data["allele"])
                messages.success(request, "Curation created.")
                curation_details_url = reverse(
                    "details_allele_curation",
                    kwargs={"curation_id": curation.curation_id},
                )
                return redirect(curation_details_url)
        else:
            form = AlleleCurationForm()
        return render(
            request,
            "curations/allele/new.html",
            {"form": form, "tabs": new_allele_curation_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:  # type: ignore
        """Renders a searchable list of allele curations.

        The view uses the `search_allele_curation_tabs` context variable to render
        navigation tabs on the page.

        Args:
            request: The Django `HttpRequest` object. The GET parameters may include `q`
                for filtering the curations.

        Returns:
            A Django `HttpResponse` object that renders the list of allele curations.
        """
        query = request.GET.get("q", None)
        selector = AlleleCurationSelector()
        curations = selector.list(query)

        # If a user has entered a search query, HTMX will issue a GET request to the
        # URL for this view. We simply return the newly filtered table of allele
        # curations. HTMX will swap in this new table.
        if request.htmx:  # type: ignore (This attribute is added by the django-htmx app.)
            template_name = "curations/includes/curation_table.html"
        else:
            template_name = "curations/allele/list.html"

        return render(
            request,
            template_name,
            {"curations": curations, "tabs": search_allele_curation_tabs},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, curation_id: str) -> HttpResponse:  # pyright: ignore[reportIncompatibleMethodOverride] (Pyright doesn't understand ABCs.)
        """Renders the details page for a specific allele curation.

        Args:
            request: The Django `HttpRequest` object.
            curation_id: A string that uniquely identifies the allele curation for
                display.

        Returns:
            A Django `HttpResponse` object that renders the allele curation's details
                page.
        """
        selector = AlleleCurationSelector()
        curation = selector.get(curation_id)
        context = {"curation": curation}
        return render(request, "curations/allele/details.html", context)
