"""Provides views for the haplotype app."""

from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from haplotype.forms import HaplotypeForm
from haplotype.models import Haplotype


class HaplotypeCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a haplotype."""

    model = Haplotype
    form_class = HaplotypeForm
    template_name = "haplotype/create.html"


class HaplotypeDetail(DetailView):
    """Shows the user information about a haplotype."""

    model = Haplotype
    template_name = "haplotype/detail.html"
