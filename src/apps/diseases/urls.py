"""Define the URLs for the `diseases` app."""

from django.urls import path

from apps.diseases.views.mondo import MondoView

view = MondoView()

urlpatterns = [
    path("mondo/new", view.new, name="new_mondo"),
    path("mondo/list", view.list, name="list_mondo"),
]
