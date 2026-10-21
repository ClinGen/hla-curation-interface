from django.urls import path

from repo import views

urlpatterns = [
    path("", views.PublishedCurationList.as_view(), name="repo-search"),
    path("about", views.about, name="repo-about"),
    path("acknowledgements", views.acknowledgements, name="repo-acknowledgements"),
    path("citing", views.citing, name="repo-citing"),
    path("collaborators", views.collaborators, name="repo-collaborators"),
    path("contact", views.contact, name="repo-contact"),
    path("help", views.help_, name="repo-help"),
    path("download/all.json", views.download_all_json, name="repo-download-all"),
    path("download/all.csv", views.download_all_csv, name="repo-download-all-csv"),
    path("download/all.xlsx", views.download_all_xlsx, name="repo-download-all-xlsx"),
    path(
        "<slug:curation_slug>/detail",
        views.PublishedCurationDetail.as_view(),
        name="repo-detail",
    ),
    path(
        "<slug:curation_slug>/scoring-summary",
        views.PublishedScoringSummary.as_view(),
        name="repo-scoring-summary",
    ),
    path(
        "<slug:curation_slug>/evidence-scoring-summary",
        views.PublishedEvidenceScoringSummary.as_view(),
        name="repo-evidence-scoring-summary",
    ),
    path(
        "<slug:curation_slug>/download.json",
        views.download_single_json,
        name="repo-download-single",
    ),
    path(
        "<slug:curation_slug>/download.csv",
        views.download_single_csv,
        name="repo-download-single-csv",
    ),
    path(
        "<slug:curation_slug>/download.xlsx",
        views.download_single_xlsx,
        name="repo-download-single-xlsx",
    ),
    path(
        "<slug:curation_slug>/evidence/<slug:evidence_slug>",
        views.PublishedEvidenceDetail.as_view(),
        name="repo-evidence",
    ),
    path(
        "<slug:curation_slug>/history",
        views.PublishedCurationHistory.as_view(),
        name="repo-history",
    ),
    path(
        "<slug:curation_slug>/history/<int:history_id>/change",
        views.PublishedCurationChange.as_view(),
        name="repo-change",
    ),
]
