"""Configures URLs for the disease app."""

from django.urls import path

from disease import views

urlpatterns = [
    path("create", views.DiseaseCreate.as_view(), name="disease-create"),
    path("<int:pk>/detail", views.DiseaseDetail.as_view(), name="disease-detail"),
    path("search", views.disease_search, name="disease-search"),
]
