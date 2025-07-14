"""Configures URLs for the curation app."""

from django.urls import path

from curation import views

urlpatterns = [
    path("create", views.CurationCreate.as_view(), name="curation-create"),
    path(
        "detail/<int:curation_pk>",
        views.CurationDetail.as_view(),
        name="curation-detail",
    ),
    path("search", views.curation_search, name="curation-search"),
    path("edit/<int:curation_pk>", views.curation_edit, name="curation-edit"),
    path(
        "<int:curation_pk>/evidence/create",
        views.EvidenceCreate.as_view(),
        name="evidence-create",
    ),
    path(
        "<int:curation_pk>/evidence/<int:evidence_pk>",
        views.EvidenceDetail.as_view(),
        name="evidence-detail",
    ),
    path(
        "<int:curation_pk>/evidence/<int:evidence_pk>/edit",
        views.EvidenceEdit.as_view(),
        name="evidence-edit",
    ),
]
