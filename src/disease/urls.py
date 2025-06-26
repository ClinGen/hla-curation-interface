"""Configures URLs for the disease app."""

from django.urls import path

from disease import views

urlpatterns = [
    path("create", views.DiseaseCreateView.as_view(), name="disease-create"),
    path("detail/<int:pk>", views.DiseaseDetailView.as_view(), name="disease-detail"),
    path("search", views.disease_search, name="disease-search"),
]
