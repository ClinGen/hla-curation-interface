"""Define the URLs for the `markers` app."""

from django.urls import path

from apps.markers.views.allele import AlleleView

view = AlleleView()

urlpatterns = [
    path("allele/new", view.new, name="new_allele"),
]
