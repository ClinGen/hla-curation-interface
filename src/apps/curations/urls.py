"""Define the URLs for the `curations` app."""

from django.urls import path

from apps.curations.views.allele import AlleleCurationView
from apps.curations.views.haplotype import HaplotypeCurationView

allele = AlleleCurationView()
haplotype = HaplotypeCurationView()

urlpatterns = [
    path("allele/new", allele.new, name="new_allele_curation"),
    path("allele/list", allele.list, name="list_allele_curation"),
    path("haplotype/new", haplotype.new, name="new_haplotype_curation"),
    path("haplotype/list", haplotype.list, name="list_haplotype_curation"),
]
