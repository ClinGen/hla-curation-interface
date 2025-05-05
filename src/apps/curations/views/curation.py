"""Provide views for curations."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.curations.forms.curation import CurationForm
from apps.curations.services.curation import CurationService
from apps.users.selectors.curator import get_curator
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
                service = CurationService()
                curator = get_curator(request.user.username)
                service.create(
                    data["curation_type"], data["disease"], data["allele"], curator
                )
                messages.success(request, "Curation created successfully.")
                return redirect("home")
        else:
            form = CurationForm()
        return render(
            request,
            "curations/new.html",
            {"form": form},
        )

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for a PubMed publication."""

    # TODO(Liam): Do the following tasks.  # noqa: FIX002, TD003
    # - Implement the method below.
    # - Remove the pyright ignore directive.
    @staticmethod
    def details(request: HttpRequest, human_readable_id: str) -> HttpResponse:  # type: ignore
        """Return the details page for a PubMed publication."""
