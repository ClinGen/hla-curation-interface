"""Defines the URLs for the `curations` app."""

from django.urls import path

from apps.curations.views.allele.association import PubMedAlleleAssociationView
from apps.curations.views.allele.curation import AlleleCurationView
from apps.curations.views.haplotype.curation import HaplotypeCurationView

allele_curation = AlleleCurationView()
allele_association = PubMedAlleleAssociationView()
haplotype_curation = HaplotypeCurationView()

urlpatterns = [
    path("allele/new", allele_curation.new, name="new_allele_curation"),
    path("allele/list", allele_curation.list, name="list_allele_curation"),
    path(
        "allele/<str:curation_id>",
        allele_curation.details,
        name="details_allele_curation",
    ),
    path(
        "allele/<str:curation_id>/association/new",
        allele_association.new,
        name="new_allele_association",
    ),
    path(
        "allele/<str:curation_id>/association/<str:association_id>/edit",
        allele_association.edit,
        name="edit_allele_association",
    ),
    path("haplotype/new", haplotype_curation.new, name="new_haplotype_curation"),
    path("haplotype/list", haplotype_curation.list, name="list_haplotype_curation"),
]
