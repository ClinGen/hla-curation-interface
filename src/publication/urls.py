"""Configures URLs for the publication app."""

from django.urls import path

from publication import views

urlpatterns = [
    path("create", views.PublicationCreateView.as_view(), name="publication-create"),
    path(
        "detail/<int:pk>",
        views.PublicationDetailView.as_view(),
        name="publication-detail",
    ),
    path("search", views.publication_search, name="publication-search"),
]
