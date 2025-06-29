"""Configures URLs for the publication app."""

from django.urls import path

from publication import views

urlpatterns = [
    path("create", views.PublicationCreate.as_view(), name="publication-create"),
    path(
        "detail/<int:pk>",
        views.PublicationDetail.as_view(),
        name="publication-detail",
    ),
    path("search", views.publication_search, name="publication-search"),
]
