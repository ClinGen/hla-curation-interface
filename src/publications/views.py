"""Provides views for the publications app."""

from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from publications.forms import PublicationForm
from publications.models import Publication


class PublicationCreateView(CreateView):
    """Allows the user to create (add) a publication."""

    model = Publication
    form_class = PublicationForm
    template_name = "publications/publication_create.html"


class PublicationDetailView(DetailView):
    """Shows the user information about a publication."""

    model = Publication
    template_name = "publications/publication_detail.html"
