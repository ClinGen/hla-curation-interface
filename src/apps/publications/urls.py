"""Define the URLs for the publications app."""

from django.urls import path

from apps.publications.views.pubmed import PubMedView

view = PubMedView()

urlpatterns = [
    path("pubmed/new", view.new, name="new_pubmed"),
    path("pubmed/list", view.list, name="list_pubmed"),
]
