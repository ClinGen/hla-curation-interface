"""Provides views for the disease app."""

from django.views.generic import CreateView, DetailView

from core.permissions import CreateAccessMixin
from disease.forms import DiseaseForm
from disease.models import Disease


class DiseaseCreateView(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a disease."""

    model = Disease
    form_class = DiseaseForm
    template_name = "disease/create.html"


class DiseaseDetailView(DetailView):
    """Shows user information about a disease."""

    model = Disease
    template_name = "disease/detail.html"
