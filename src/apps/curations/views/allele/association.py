"""Provides HTTP views for managing allele associations within the application.

This module is meant to handle primarily HTTP logic. Read logic should be delegated to
the relevant selectors module. Create and update logic should be delegated to the
relevant services module.

This module defines views for creating new allele associations, listing existing ones
with search functionality, and displaying detailed information for a specific
allele association. These views handle user interactions, form processing,
data retrieval via selectors, and data manipulation via services related to
allele curations.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from apps.curations.forms.allele.pubmed_association import PubMedAlleleAssociationForm
from apps.curations.selectors.allele.association import PubMedAlleleAssociationSelector
from apps.curations.services.allele.association import AlleleAssociationService
from apps.users.permissions.crud import can_delete
from base.views import EntityView
from constants import HPOConstants, PublicationTypeConstants


class PubMedAlleleAssociationView(EntityView):
    """Encapsulates the primary interactions for PubMed allele associations.

    This class provides methods for:
        - Creating new allele associations based on user input.
        - Displaying a searchable list of existing allele associations.
        - Showing detailed information for a specific allele association.
    """

    @staticmethod
    @login_required
    def new(request: HttpRequest, curation_id: str) -> HttpResponse:
        """Renders the new association form and handles the form's submission.

        Args:
            request: The Django `HttpRequest` object.
            curation_id: The human-readable ID of the curation for the association.

        Returns:
            A Django `HttpResponse` object rendering the form.
        """
        if request.method == "POST":
            service = AlleleAssociationService()
            publication_type = request.POST.get("publication_type")
            association = service.create(curation_id, publication_type)
            if association:
                messages.success(request, "Association created.")
                association_edit_url = reverse(
                    "edit_allele_association",
                    kwargs={
                        "curation_id": curation_id,
                        "association_id": association.association_id,
                    },
                )
                response = HttpResponse(status=204)
                response["HX-Redirect"] = association_edit_url
                response["HX-Replace-Url"] = "true"
                return response
        messages.error(request, "Unable to create association.")
        curation_details_url = reverse(
            "details_allele_curation", kwargs={"curation_id": curation_id}
        )
        return redirect(curation_details_url)

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    # - Remove the lint ignore directive.
    @staticmethod
    def list(request: HttpRequest) -> None:  # type: ignore  # noqa: ARG004
        """Renders a searchable list of PubMed allele associations."""

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    # - Remove the lint ignore directive.
    @staticmethod
    def details(request: HttpRequest, association_id: str) -> None:  # pyright: ignore[reportIncompatibleMethodOverride] (Pyright doesn't understand ABCs.)
        """Renders the details page for a specific PubMed allele association."""

    @staticmethod
    @never_cache
    def edit(
        request: HttpRequest, curation_id: str, association_id: str
    ) -> HttpResponse:
        """Renders the edit page for a specific PubMed allele curation.

        Args:
            request: The Django `HttpRequest` object.
            curation_id: The human-readable ID of the curation for the association.
            association_id: The human-readable ID of the association.

        Returns:
            A Django `HttpResponse` object rendering the form.
        """
        selector = PubMedAlleleAssociationSelector()
        association = selector.get(human_readable_id=association_id)
        if not association:
            return redirect("details_allele_curation", curation_id=curation_id)

        form = PubMedAlleleAssociationForm(instance=association)
        if request.method == "POST":
            form = PubMedAlleleAssociationForm(request.POST, instance=association)
            if form.is_valid():
                form.save()
                messages.success(request, "All changes saved.")
                edit_allele_curation_url = reverse(
                    "edit_allele_association",
                    kwargs={
                        "curation_id": curation_id,
                        "association_id": association_id,
                    },
                )
                response = HttpResponse(status=204)
                # Reset the user's scroll position.
                response["HX-Redirect"] = edit_allele_curation_url
                response["HX-Replace-Url"] = "true"
                return response
            messages.error(request, "Please fix the errors in the form.")

        # Prepare the context with the form
        context = {
            "form": form,
            "association": association,
            "curation_id": curation_id,
            "hpo_search_url": HPOConstants.SEARCH_URL,
        }
        return render(request, "associations/allele/pubmed/edit.html", context)

    @staticmethod
    def delete(
        request: HttpRequest, curation_id: str, association_id: str
    ) -> HttpResponse:
        """Deletes the PubMed allele association.

        Args:
            request: The Django `HttpRequest` object.
            curation_id: The human-readable ID of the curation for the association.
            association_id: The human-readable ID of the association.

        Returns:
            A Django `HttpResponse` object.
        """
        if request.method == "DELETE" and can_delete(request.user):
            service = AlleleAssociationService()
            service.delete(association_id, PublicationTypeConstants.PUBMED)
            messages.success(request, "Association deleted.")
            allele_curation_details_url = reverse(
                "details_allele_curation", kwargs={"curation_id": curation_id}
            )
            response = HttpResponse(status=204)
            # Reset the user's scroll position.
            response["HX-Redirect"] = allele_curation_details_url
            response["HX-Replace-Url"] = "true"
            return response
        messages.warning(
            request, "You do not have the correct permissions to delete an association."
        )
        return redirect(
            "edit_allele_association",
            curation_id=curation_id,
            association_id=association_id,
        )
