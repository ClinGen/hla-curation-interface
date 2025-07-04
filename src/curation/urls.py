"""Configures URLs for the curation app."""

from django.urls import path

from curation import views

urlpatterns = [
    path("create", views.CurationCreate.as_view(), name="curation-create"),
    path("detail/<int:pk>", views.CurationDetail.as_view(), name="curation-detail"),
    path("search", views.curation_search, name="curation-search"),
]
