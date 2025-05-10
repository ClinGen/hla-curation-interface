"""Provide the home view for the HCI."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.curations.models.allele.curation import AlleleCuration
from apps.users.models.curator import Curator


def home(request: HttpRequest) -> HttpResponse:
    """View the home page of the HCI.

    The home page can be thought of as the main hub of the HCI. It is where the user can
    view their curations and their affiliation's curations. It also has links to the
    other pages of the HCI.

    Returns:
        The rendered home page.
    """
    # TODO(Liam): Use selectors.  # noqa: FIX002, TD003
    curator = None
    if request.user.is_authenticated:
        curator = Curator.objects.get(user=request.user)
        allele_curations = AlleleCuration.objects.filter(created_by=curator)
    else:
        allele_curations = AlleleCuration.objects.all()
    context = {
        "curator": curator,
        "allele_curations": allele_curations,
    }
    return render(request, "home/index.html", context)
