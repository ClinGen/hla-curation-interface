"""Provide a profile page view."""

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.users.selectors.affiliation import get_affiliation
from apps.users.selectors.curator import get_curator
from constants import AffiliationsConstants


@login_required
def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Return the user's profile page."""
    curator = get_curator(username)
    affiliation = get_affiliation(affiliation_id=AffiliationsConstants.DEFAULT_ID)
    return render(
        request, "users/profile.html", {"curator": curator, "affiliation": affiliation}
    )
