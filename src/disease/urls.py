from django.urls import path

from disease import views
from disease.views import DiseaseList

urlpatterns = [
    path("create", views.DiseaseCreate.as_view(), name="disease-create"),
    path("<slug:slug>/detail", views.DiseaseDetail.as_view(), name="disease-detail"),
    path("list", DiseaseList.as_view(), name="disease-list"),
]
