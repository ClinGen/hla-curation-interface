"""Define the URLs for the `curations` app."""

from django.urls import path

from apps.curations.views.curation import CurationView

view = CurationView()

urlpatterns = [
    path("curation/new", view.new, name="new_curation"),
]
