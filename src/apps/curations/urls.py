"""Define the URLs for the curations app."""

from django.urls import path

from apps.curations.views.curation import edit

urlpatterns = [
    path("curation/edit", edit, name="edit"),
]
