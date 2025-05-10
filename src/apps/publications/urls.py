"""Define the URLs for the publications app."""

from django.urls import path

from apps.publications.views.biorxiv import RxivBioView
from apps.publications.views.medrxiv import RxivMedView
from apps.publications.views.pubmed import PubMedView

pubmed = PubMedView()
biorxiv = RxivBioView()
medrxiv = RxivMedView()

urlpatterns = [
    path("pubmed/new", pubmed.new, name="new_pubmed"),
    path("pubmed/list", pubmed.list, name="list_pubmed"),
    path("pubmed/<str:pubmed_id>/details", pubmed.details, name="details_pubmed"),
    path("biorxiv/new", biorxiv.new, name="new_biorxiv"),
    path("biorxiv/list", biorxiv.list, name="list_biorxiv"),
    path("medrxiv/new", medrxiv.new, name="new_medrxiv"),
    path("medrxiv/list", medrxiv.list, name="list_medrxiv"),
]
