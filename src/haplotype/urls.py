"""Configures URLs for the haplotype app."""

from django.urls import path

from haplotype import views

urlpatterns = [
    path("create", views.HaplotypeCreate.as_view(), name="haplotype-create"),
    path("<int:pk>/detail", views.HaplotypeDetail.as_view(), name="haplotype-detail"),
    path("search", views.haplotype_search, name="haplotype-search"),
]
