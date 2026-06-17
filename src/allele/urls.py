from django.urls import path

from allele import views
from allele.views import AlleleList

urlpatterns = [
    path("create", views.AlleleCreate.as_view(), name="allele-create"),
    path("<slug:slug>/detail", views.AlleleDetail.as_view(), name="allele-detail"),
    path("<slug:slug>/history", views.AlleleHistory.as_view(), name="allele-history"),
    path(
        "<slug:slug>/history/<int:history_id>/change",
        views.AlleleChange.as_view(),
        name="allele-change",
    ),
    path("list", AlleleList.as_view(), name="allele-list"),
]
