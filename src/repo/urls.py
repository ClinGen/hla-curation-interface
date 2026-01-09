"""Configures URLs for the repo app."""

from django.urls import path

from repo import views

urlpatterns = [
    path("", views.repo_search, name="repo-search"),
    path("download/all.json", views.download_all_json, name="repo-download-all"),
    path(
        "<slug:curation_slug>/detail",
        views.PublishedCurationDetail.as_view(),
        name="repo-detail",
    ),
    path(
        "<slug:curation_slug>/download.json",
        views.download_single_json,
        name="repo-download-single",
    ),
]
