from django.urls import path

from curation import views
from curation.views import CurationList

urlpatterns = [
    path(
        "create",
        views.CurationCreate.as_view(),
        name="curation-create",
    ),
    path(
        "<slug:curation_slug>/detail",
        views.CurationDetail.as_view(),
        name="curation-detail",
    ),
    path(
        "list",
        CurationList.as_view(),
        name="curation-list",
    ),
    path(
        "<slug:curation_slug>/edit-curation",
        views.CurationEdit.as_view(),
        name="curation-edit",
    ),
    path(
        "<slug:curation_slug>/edit-evidence",
        views.curation_edit_evidence,
        name="curation-edit-evidence",
    ),
    path(
        "<slug:curation_slug>/publish",
        views.curation_publish,
        name="curation-publish",
    ),
    path(
        "<slug:curation_slug>/evidence/create",
        views.EvidenceCreate.as_view(),
        name="evidence-create",
    ),
    path(
        "<slug:curation_slug>/evidence/<slug:evidence_slug>/detail",
        views.EvidenceDetail.as_view(),
        name="evidence-detail",
    ),
    path(
        "<slug:curation_slug>/evidence/<slug:evidence_slug>/edit",
        views.EvidenceEdit.as_view(),
        name="evidence-edit",
    ),
]
