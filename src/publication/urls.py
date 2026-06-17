from django.urls import path

from publication import views
from publication.views import PublicationList

urlpatterns = [
    path("create", views.PublicationCreate.as_view(), name="publication-create"),
    path(
        "<slug:slug>/detail",
        views.PublicationDetail.as_view(),
        name="publication-detail",
    ),
    path(
        "<slug:slug>/history",
        views.PublicationHistory.as_view(),
        name="publication-history",
    ),
    path(
        "<slug:slug>/history/<int:history_id>/change",
        views.PublicationChange.as_view(),
        name="publication-change",
    ),
    path("list", PublicationList.as_view(), name="publication-list"),
]
