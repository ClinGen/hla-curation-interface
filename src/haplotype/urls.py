"""Configures URLs for the haplotype app."""

from django.urls import path

from haplotype import views

urlpatterns = [
    path("create", views.HaplotypeCreate.as_view(), name="haplotype-create"),
    path("detail/<int:pk>", views.HaplotypeDetail.as_view(), name="haplotype-detail"),
]
