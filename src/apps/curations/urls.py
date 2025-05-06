"""Define the URLs for the `curations` app."""

from django.urls import path

from apps.curations.views.curation import CurationView

view = CurationView()

urlpatterns = [
    path("new", view.new, name="new_curation"),
    path("list", view.list, name="list_curation"),
]
