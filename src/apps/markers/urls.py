"""Define the URLs for the `markers` app."""

from django.urls import path

from apps.markers.views.allele import AlleleView
from apps.markers.views.haplotype import HaplotypeView

allele = AlleleView()
haplotype = HaplotypeView()

urlpatterns = [
    path("allele/new", allele.new, name="new_allele"),
    path("allele/list", allele.list, name="list_allele"),
    path("haplotype/new", haplotype.new, name="new_haplotype"),
    path("haplotype/list", haplotype.list, name="list_haplotype"),
]
