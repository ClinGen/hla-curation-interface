from django.urls import path

from disease import views
from disease.views import DiseaseList

urlpatterns = [
    path("create", views.DiseaseCreate.as_view(), name="disease-create"),
    path("<slug:slug>/detail", views.DiseaseDetail.as_view(), name="disease-detail"),
    path("<slug:slug>/history", views.DiseaseHistory.as_view(), name="disease-history"),
    path(
        "<slug:slug>/history/<int:history_id>/change",
        views.DiseaseChange.as_view(),
        name="disease-change",
    ),
    path("list", DiseaseList.as_view(), name="disease-list"),
]
