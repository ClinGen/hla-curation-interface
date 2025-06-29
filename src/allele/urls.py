"""Configures URLs for the allele app."""

from django.urls import path

from allele import views

urlpatterns = [
    path("create", views.AlleleCreateView.as_view(), name="allele-create"),
    path("detail/<int:pk>", views.AlleleDetailView.as_view(), name="allele-detail"),
    path("search", views.allele_search, name="allele-search"),
]
