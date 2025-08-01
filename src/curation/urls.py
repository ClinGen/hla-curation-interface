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
    path(
        "<int:curation_pk>/edit-curation",
        views.CurationEdit.as_view(),
        name="curation-edit",
    ),
    path(
        "<int:curation_pk>/edit-evidence",
        views.curation_edit_evidence,
        name="curation-edit-evidence",
    ),
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
