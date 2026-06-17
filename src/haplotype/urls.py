from django.urls import path

from haplotype import views
from haplotype.views import HaplotypeList

urlpatterns = [
    path("create", views.HaplotypeCreate.as_view(), name="haplotype-create"),
    path(
        "<slug:slug>/detail", views.HaplotypeDetail.as_view(), name="haplotype-detail"
    ),
    path(
        "<slug:slug>/history",
        views.HaplotypeHistory.as_view(),
        name="haplotype-history",
    ),
    path(
        "<slug:slug>/history/<int:history_id>/change",
        views.HaplotypeChange.as_view(),
        name="haplotype-change",
    ),
    path("list", HaplotypeList.as_view(), name="haplotype-list"),
]
